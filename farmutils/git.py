import subprocess
from os import chdir
import re

from farmutils.helpers import run_host_cmd


class InvalidVersionSpecifier(Exception):
    pass


class InvalidBranch(Exception):
    pass


def reset_repos(base_dir, repos, tag, default_tag=None, log_func=print):
    for repo in repos:
        log_func('Resetting repo [{}] to tag [{}]...'.format(repo, tag))
        chdir('{}/{}'.format(base_dir, repo))
        run_host_cmd("git fetch --all")
        try:
            run_host_cmd("git reset --hard {}".format(tag))
        except subprocess.CalledProcessError as e:
            if tag == default_tag or default_tag is None:
                log_func("Failed to reset repo [{}] to tag [{}]".format(
                    repo, tag))
                raise e
            else:
                log_func("Failed to reset repo [{}] to [{}] - so using default [{}]".format(
                    repo, tag, default_tag))
                run_host_cmd("git reset --hard {}".format(default_tag))


def get_latest_tag(srcdir, branch):
    chdir(srcdir)
    run_host_cmd("git fetch --all")
    tag, rc = run_host_cmd("git describe origin/{}".format(branch))
    return tag.rstrip()


def get_tag_list(srcdir):
    chdir(srcdir)
    result, __ = run_host_cmd("git tag -l")
    return None if not result else result.split('\n')


def version_is_valid(version, pattern=None):
    '''
    Check that @version string matches regex @pattern.
    If no pattern given, the regex used is: ^[0-9]{1,4}\.[0-9]{1,4}\.[0-9]{1,4}$
    This corresponds to: major.minor.revision, x.y.z
    '''

    pattern = pattern or '^[0-9]{1,4}\.[0-9]{1,4}\.[0-9]{1,4}$'

    return True if re.search(pattern, version) else False


def filter_versions(versions, v_filter):
    '''
    Returns a list of all @versions that match the version filter
    @v_filter. If no matching versions, returns None.

    Filters should be of the form:
    '': match all versions
    '+y' : match up to the first y versions
    '-y' : match up to the last y versions
    'x.x.x': match only version x.x.x
    'x.x.x !': match all versions except x.x.x
    'x.x.x +': match version x.x.x, and all subsequent versions
    'x.x.x -': match version x.x.x, and all previous versions
    'x.x.x +y': match version x.x.x, and up to y subsequent versions
    'x.x.x -y': match version x.x.x, and up to y previous versions
    '''

    invalid_versions = list(filter(lambda v: not version_is_valid(v), versions))
    if invalid_versions:
        raise InvalidVersionSpecifier('Invalid versions: {}'.format(
            invalid_versions))

    # Strip spaces
    v_filter = v_filter.replace(' ', '')

    # Convert version strings to tuples of (major, minor, revision)
    versions = list(map(lambda v: tuple(v.split('.')), versions))

    # Sort versions
    versions.sort()

    v_pattern = '[0-9]{1,4}\.[0-9]{1,4}\.[0-9]{1,4}'

    # Get reference version
    v_ref_match = re.match(v_pattern, v_filter)

    # Remove versions that do not match the filter
    if v_ref_match:
        v_ref_str = v_ref_match.group()
        v_ref = tuple(v_ref_str.split('.'))

        # Version condition is everything not the reference version
        v_cond = v_filter.replace(v_ref_str, '')

        # 'x.x.x': match only version x.x.x
        if v_cond == '':
            versions = [v_ref] if v_ref in versions else None

        else:
            cond_pattern = '^[!\-+][0-9]*$'
            if not re.match(cond_pattern, v_cond):
                raise InvalidVersionSpecifier('Invalid condition [{}] in filter [{}]'.format(
                    v_cond, v_filter))

            # 'x.x.x !': match all versions except x.x.x
            if v_cond == '!' and v_ref in versions:
                versions.remove(v_ref)

            # 'x.x.x -': match version x.x.x, and all previous versions
            elif '-' in v_cond:
                versions = [v for v in versions if v <= v_ref]
                v_cond = v_cond.replace('-', '')

                # 'x.x.x -y': match version x.x.x, and up to y previous versions
                if v_cond and len(versions) > int(v_cond):
                    versions = versions[-int(v_cond):]

            # 'x.x.x +': match version x.x.x, and all subsequent versions
            elif '+' in v_cond:
                versions = [v for v in versions if v >= v_ref]
                v_cond = v_cond.replace('+', '')

                # 'x.x.x +y': match version x.x.x, and up to y subsequent versions
                if v_cond and len(versions) > int(v_cond):
                    versions = versions[:int(v_cond)]

    else:
        # '': match all versions
        if v_filter == '':
            pass

        else:
            v_cond = v_filter

            cond_pattern = '^[\-+][0-9]*$'
            if not re.match(cond_pattern, v_cond):
                raise InvalidVersionSpecifier('Invalid filter [{}]'.format(
                    v_filter))

            # '-y' : match up to the last y versions
            if '-' in v_cond:
                v_cond = v_cond.replace('-', '')
                if v_cond and len(versions) > int(v_cond):
                    versions = versions[-int(v_cond):]

            # '+y' : match up to the first y versions
            elif '+' in v_cond:
                v_cond = v_cond.replace('+', '')
                if v_cond and len(versions) > int(v_cond):
                    versions = versions[:int(v_cond)]


    # convert version tuple list back to version strings
    versions = None if not versions else list(map(lambda v: '{}.{}.{}'.format(v[0], v[1], v[2]), versions))

    return versions

def compile_version_list(srcdir, version_filters):
    '''
    Compile a list of versions in the git repository at @srcdir that matches
    the @version_filters.

    Returns a list of all upstream tags which match the pattern
    major.minor.revision, and match the version filters.
    If there are no matching versions, None is returned.

    All whitespace will be stripped from version_filters.

    Filters should be of the form:
    'x.x.x': match only version x.x.x
    '! x.x.x': match all versions except x.x.x
    'x.x.x +': match version x.x.x, and all subsequent versions
    'x.x.x -': match version x.x.x, and all previous versions
    'x.x.x +y': match version x.x.x, and up to y subsequent versions
    'x.x.x -y': match version x.x.x, and up to y previous versions
    '+y' : match up to the first y versions
    '-y' : match up to the last y versions

    One or more filters can be applied, separated by '&'. If more than one
    filter is given then only versions matching all filters will be returned.
    E.g. To get a list of upstream tags in range 1.1.100 - 1.1.200:
    version_filters = '1.1.100+ & 1.1.200-'

    '''
    if not version_filters:
        return None

    # Strip spaces
    version_filters = version_filters.replace(' ', '')

    all_tags = get_tag_list(srcdir)

    if not all_tags:
        return None

    # Filter out any tags that are not valid version strings
    all_versions = list(filter(lambda t: version_is_valid(t), all_tags))

    if not all_versions:
        return None

    # Convert version filters to a list
    if '&' in version_filters:
        version_filters = version_filters.split('&')
    else:
        version_filters = [version_filters]

    filtered_versions_lists = [filter_versions(all_versions, f) for f in version_filters]

    if None in filtered_versions_lists:
        return None

    if filtered_versions_lists:
        filtered_versions = set(filtered_versions_lists[0])
        for v in filtered_versions_lists[1:]:
            filtered_versions.intersection_update(v)

        filtered_versions = list(filtered_versions)
    else:
        filtered_versions = None

    return filtered_versions or None


