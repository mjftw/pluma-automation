from farmutils import git

#
# Really needs a set of farm-test repo(s) with/without tags, tags with python unfriendly characters, known and missing branches (maybe no master), etc.
#

def test_get_latest_tag():
    tag = git.get_latest_tag(".", "master")
    print(tag)

def test_get_tag_list():
    taglist = git.get_tag_list(".")
    print(taglist)

def test_reset_repos():
    # fails due to None
    # can fail (for non-git reasons) depending on current working directory
    git.reset_repos("..", ["farm-documentation"], None)

def main():
    # fails in farm-core -- no tags
    # succeeds in ovation/fb4_wizard
    try:
        test_get_latest_tag()
    except Exception as e: 
        print("Exception: " + str(e))

    try:
        test_get_tag_list()
    except Exception as e: 
        print("Exception: " + str(e))

    try:
        test_reset_repos()
    except Exception as e: 
        print("Exception: " + str(e))

if __name__ == '__main__':
    main()
