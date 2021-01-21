import base64
import json
import requests
import time
import json
import magic
import gzip
from datetime import datetime
from requests.auth import AuthBase
from atlassian import Jira
from dataclasses import dataclass
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional


@contextmanager
def _attachement(filename):
    tmp_file = ""
    mime = magic.from_file(str(filename), mime=True)
    if (Path(filename).stat().st_size > 10*1024) and mime == 'text/plain':
        tmp_file = f'{filename}.gz'
        with gzip.open(tmp_file, "wb") as gz:
            with open(filename, "rb") as f:
                gz.write(f.read())
        yield (tmp_file, 'application/gzip')
    else:
        yield (filename, mime)

    if tmp_file:
        Path(tmp_file).unlink()


@contextmanager
def _attachement_from_string(s):
    mime = magic.from_buffer(s, mime=True)
    compressed = None
    if (len(s) > 10*1024) and mime == 'text/plain':
        compressed = gzip.compress(s)
        yield (compressed, 'application/gzip')
    else:
        yield (s, mime)

    if compressed:
        del compressed


class _BearerAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


class Xray:
    def __init__(self, client_id, client_secret, project_key) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.project_key = project_key
        self.token = None

    def xray_athenticate(self, force=False):
        if not force and self.token:
            return self.token

        resp = requests.post(
            url="https://xray.cloud.xpand-it.com/api/v2/authenticate",
            data={"client_id": self.client_id,
                  "client_secret": self.client_secret}
        )
        if not resp.ok:
            raise Exception(f"XRay authentication failed. {resp}")
        self.token = resp.text[1:-1]
        return self.token

    def create_or_update_test_execution(self, test_execution_info, test_exec_key=None, tests=[]):
        xray_token = self.xray_athenticate()

        data = {"info": test_execution_info, "tests": tests}
        if test_exec_key:
            data["testExecutionKey"] = test_exec_key
        resp = requests.post(
            url=f" https://xray.cloud.xpand-it.com/api/v2/import/execution",
            auth=_BearerAuth(xray_token),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data)
        )
        if not resp.ok:
            raise Exception(f"creating test execution in XRay failed.\n{resp}\n{resp.text}")
        d = json.loads(resp.text)
        return d["key"]

    # def update_test_execution(self, test_exec_key, tests, info = None):
    #     xray_token = self.xray_athenticate()
    #     if info:
    #         data = json.dumps({"testExecutionKey": test_exec_key, "info": info, "tests": tests})
    #     else:
    #         data = json.dumps({"testExecutionKey": test_exec_key, "tests": tests})
    #     resp = requests.post(
    #         url = f" https://xray.cloud.xpand-it.com/api/v2/import/execution",
    #         auth = BearerAuth(xray_token),
    #         headers = {'Content-Type': 'application/json'},
    #         data = data
    #     )
    #     if not resp.ok:
    #         raise Exception(f"creating test execution in XRay failed.\n{resp}\n{resp.text}")
    #     d = json.loads(resp.text)
    #     return d["key"]

    def import_tests(self, bulk_data):
        # logging.debug("sending test definitions to xray")
        xray_token = self.xray_athenticate()
        resp = requests.post(
            url=f"https://xray.cloud.xpand-it.com//api/v2/import/test/bulk?project={self.project_key}",
            auth=_BearerAuth(xray_token),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(bulk_data)
        )
        if not resp.ok:
            raise Exception(f"importing test definition in XRay failed.\n{resp}\n{resp.text}")
        d = json.loads(resp.text)
        jobid = d["jobId"]
        while True:
            resp = None
            sleep_time = 1
            for i in range(5):
                time.sleep(sleep_time)
                sleep_time += 1
                url = f"https://xray.cloud.xpand-it.com/api/v2/import/test/bulk/{jobid}/status"
                resp = requests.get(url=url, auth=_BearerAuth(xray_token))
                if resp.ok:
                    break
            if not resp or not resp.ok:
                raise Exception("Cannot get the import status")
            d = json.loads(resp.text)
            status = d["status"]
            if status != "pending" and status != "working":
                break
        if status == "unsuccessful" or status == "failed":
            raise Exception(
                f"Cannot import any test definition.\n response: {resp}. {resp.text}")
        if status == "partially_successful":
            raise Exception(
                "Cannot import all test definitions.\n response: {resp}")


@dataclass
class JiraResult:
    name: str
    startDate: datetime
    stopDate: datetime
    status: str
    summary: str = ''
    comment: str = ''
    description: str = ''
    log: str = ''

    requirements: list = []
    attachments: list = []
    steps: list = []
    key: Optional[str] = None

    def to_xray_format(self):
        evidences = []
        if self.log:
            evidences.append(JiraXrayHelper.str_to_evidence(self.log, "log.txt"))
        # for f in self.attachments:
        #    evidences.append(JiraXrayHelper.file_to_evidence(f))

        d = {
            "testKey": self.key,
            "status": self.status,
            "comment": self.comment,
            "start": self.startDate.astimezone().replace(microsecond=0).isoformat(),
            "finish": self.stopDate.astimezone().replace(microsecond=0).isoformat(),
        }
        if evidences:
            d["evidences"] = evidences

        if self.steps:
            d["steps"] = [s.to_xray_format() for s in self.steps]
        return d


@dataclass
class JiraTestPlanIssue:
    summary: str
    description: str
    key: str
    project_key: str


class JiraXrayHelper:
    @staticmethod
    def str_to_evidence(s, filename):
        if not s:
            return {}
        with _attachement_from_string(s.encode('utf-8')) as (data, mime):
            return {
                "data": base64.b64encode(data).decode('utf-8'),
                "filename": f"{filename}.gz" if mime == 'application/gzip' else f"{filename}",
                "contentType": mime
            }

    @staticmethod
    def file_to_evidence(filename, contentType):
        return {}
        # {}
        #     "data": base64.b64encode(s.encode('utf-8')).decode('utf-8'),
        #     "filename": f"{filename}",
        #     "contentType": f"{contentType}"
        # }

    @staticmethod
    def date_to_xray_format(date: datetime) -> str:
        return date.astimezone().replace(microsecond=0).isoformat()

    def __init__(self, project_key: str, jira_url: str, jira_user: str, jira_password: str, xray_client_id: str, xray_client_secret,
                 force_new_exec=False, can_delete_links=False) -> None:

        self.force_new_exec = force_new_exec
        self.can_delete_links = can_delete_links
        self.jira = Jira(url=jira_url, username=jira_user,
                         password=jira_password)
        self.xray = Xray(project_key=project_key,
                         client_id=xray_client_id, client_secret=xray_client_secret)
        self.project_key = project_key

    def add_attachment(self, issue_key, filename):
        with _attachement(filename) as (f, mime):
            self.jira.add_attachment(issue_key=issue_key, filename=f)

    def get_issues(self, jql, fields="*all", start=0, limit=None, expand=None):
        issues = []
        next_start = start
        next_limit = limit
        while True:
            if limit:
                next_limit = limit - next_start
            resp = self.jira.jql(jql, fields, start=next_start,
                                 limit=next_limit, expand=expand)
            nb_received = len(resp["issues"])
            if nb_received == 0:
                break
            next_start += nb_received
            issues.extend(resp["issues"])
        return issues

    def create_or_update_plan(self, name, description):
        def get_existing_test_plans():
            # Get all automated tests with description and labels
            jql = f'project = {self.project_key} AND issuetype = "Test Plan" order by created DESC'
            issues = self.get_issues(
                jql, fields=["summary", "description"], expand=None)
            return [JiraTestPlanIssue(summary=e["fields"]["summary"], description=e["fields"]["description"], key=e["key"], project_key=self.project_key) for e in issues]

        def find_test_plan(name, existing_test_plans):
            for t in existing_test_plans:
                if name == t.summary:
                    return t
            return None

        def create_test_plan():
            fields = {
                "project": {"key": self.project_key},
                "issuetype": {"name": "Test Plan"},
                "summary": name,
                "description": description,
            }
            d = self.jira.create_issue(fields)
            return d["key"]

        def update_test_plan(plan):
            fields = {}
            if plan.summary != name:
                fields["summary"] = name
            if plan.description != description:
                fields["description"] = description
            if fields:
                self.jira.update_issue_field(plan.key, fields)

        # at this point all tests have created and we have their IDs
        # we can start pushing the resulss
        plan = find_test_plan(name, get_existing_test_plans())
        if not plan:
            create_test_plan()
            plan = find_test_plan(name, get_existing_test_plans())
        else:
            update_test_plan(plan)

        return plan

    def create_or_update_test_execution(self, plan, xray_test_exec_info, xrays_tests: List[JiraResult], cur_execution_key=None):

        @dataclass
        class JiraTestIssue:
            summary: str
            description: str
            labels: list
            key: str
            requirements: list

        def get_existing_automated_test(project_key):
            # Get all automated tests with description and labels
            jql = f'project = {project_key} AND issuetype = Test AND labels in (testauto) order by created DESC'
            issues = self.get_issues(
                jql, fields=["summary", "description", "labels", "issuelinks"], expand=None)
            return [JiraTestIssue(
                summary=e["fields"]["summary"],
                description=e["fields"]["description"],
                key=e["key"],
                labels=e["fields"]["labels"],
                requirements={l["outwardIssue"]["key"]: l["id"]
                              for l in e["fields"]["issuelinks"] if l["type"]["name"] == "Test"}
            ) for e in issues]

        def find_by_label_in_existing_tests(label, existing_tests):
            for t in existing_tests:
                if label in t.labels:
                    return t
            return None

        def update_test(test, et):
            fields = {}
            if et.summary != test.summary:
                fields["summary"] = test.summary
            if et.description != test.description:
                fields["description"] = test.description
            if fields:
                # logging.debug(f"need to update {test.name}")
                self.jira.update_issue_field(et.key, fields=fields)

        def update_test_requirements(test, et):
            actual_req = set(test.requirements)
            jira_req = {key for key in et.requirements}
            new_req = actual_req.difference(jira_req)
            deprecated_req = jira_req.difference(actual_req)
            for req_key in new_req:
                self.jira.create_issue_link(data={
                    "type": {"name": "Test"},
                    "inwardIssue": {"key": f'{et.key}'},
                    "outwardIssue": {"key": f'{req_key}'}
                })
            for req_key in deprecated_req:
                if self.can_delete_links:
                    self.jira.remove_issue_link(et.requirements[req_key])
                else:
                    pass
                    # logging.warning(f'Issue link: "{req_key} is tested by {et.key}" should be removed')

        def find_test_execution(project_key, info):
            jql = f'project = {project_key} AND issuetype = "Test Execution" AND summary ~ "{info["summary"]}"  order by created DESC'
            issues = self.get_issues(jql, fields=["description"], expand=None)
            for text_exec in issues:
                if text_exec["fields"]["description"] == info["description"]:
                    return text_exec["key"]
            return None

        s = xray_test_exec_info["startDate"]
        modified_desc = xray_test_exec_info["description"] + f"\nStartDate: {s}"
        info = {
            "summary": xray_test_exec_info["summary"],
            "description": modified_desc,
            "startDate": xray_test_exec_info["startDate"],
            "finishDate": xray_test_exec_info["finishDate"],
            "testPlanKey": plan.key,
        }

        if self.force_new_exec:
            test_exec_key = None
        elif cur_execution_key is None:
            test_exec_key = find_test_execution(self.project_key, info)
            # This line was disabled from planrunner. Disabling this allows
            # this function to push updates to a test execution.
            # if text_exec_key:
            # logging.error("Test execution already exists... Skipping it")
            # return
        else:
            test_exec_key = cur_execution_key

        # frist identify tests from the run that are not yet JIRA issues
        existing_tests = get_existing_automated_test(plan.project_key)
        bulk_data = []
        for t in xrays_tests:
            et = find_by_label_in_existing_tests(t.name, existing_tests)
            if not et:
                bulk_data.append(
                    {
                        "testtype": "Manual",
                        "fields": {
                            "summary": f'{t.summary}',
                            "project": {"key": f'{self.project_key}'},
                            "labels":  ["testauto", f'{t.name}']
                        },
                        "steps": [
                            {"action": step.action}
                            for step in t.steps
                        ]
                    })
        if bulk_data:
            self.xray.import_tests(bulk_data)

        existing_tests = get_existing_automated_test(plan.project_key)
        for t in xrays_tests:
            et = find_by_label_in_existing_tests(t.name, existing_tests)
            update_test(t, et)
            update_test_requirements(t, et)
            t.key = et.key

        return self.xray.create_or_update_test_execution(
            info,
            test_exec_key=test_exec_key,
            tests=[t.to_xray_format() for t in xrays_tests]
        )
