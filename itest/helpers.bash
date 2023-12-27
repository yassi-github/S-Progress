################
#  run_helper  #  Invoke args, with timeout, using BATS 'run'
################
#
# Second, we use 'timeout' to abort (with a diagnostic) if something
# takes too long; this is preferable to a CI hang.
#
# Third, we log the command run and its output. This doesn't normally
# appear in BATS output, but it will if there's an error.
#
# Next, we check exit status. Since the normal desired code is 0,
# that's the default; but the expected_rc var can override:
#
#     expected_rc=125 run_helper nonexistent-subcommand
#     expected_rc=?   run_helper some-other-command       # let our caller check status
#
# Since we use the BATS 'run' mechanism, $output and $status will be
# defined for our caller.
#
function run_helper() {
    # expected_rc if unset set default to 0
    expected_rc="${expected_rc-0}"
    if [ "$expected_rc" == "?" ]; then
        expected_rc=
    fi
    # Remember command args, for possible use in later diagnostic messages
    MOST_RECENT_COMMAND="$*"

    # stdout is only emitted upon error; this echo is to help a debugger
    echo "$_LOG_PROMPT $*"

    # BATS hangs if a subprocess remains and keeps FD 3 open; this happens
    # if a process crashes unexpectedly without cleaning up subprocesses.
    run timeout -k 10 10 "$@" 3>/dev/null
    # without "quotes", multiple lines are glommed together into one
    if [ -n "$output" ]; then
        echo "$output"
    fi
    if [ "$status" -ne 0 ]; then
        echo -n "[ rc=$status "
        if [ -n "$expected_rc" ]; then
            if [ "$status" -eq "$expected_rc" ]; then
                echo -n "(expected) "
            else
                echo -n "(** EXPECTED $expected_rc **) "
            fi
        fi
        echo "]"
    fi

    if [ "$status" -eq 124 ]; then
        if expr "$output" : ".*timeout: sending" >/dev/null; then
            # It's possible for a subtest to _want_ a timeout
            if [[ "$expected_rc" != "124" ]]; then
                echo "*** TIMED OUT ***"
                false
            fi
        fi
    fi

    if [ -n "$expected_rc" ]; then
        if [ "$status" -ne "$expected_rc" ]; then
            die "exit code is $status; expected $expected_rc"
        fi
    fi

    # unset
    unset expected_rc
}

#########
#  die  #  Abort with helpful message
#########
# 
# $@: messages
function die() {
    echo "\
#/vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
#| FAIL: $*
#\\^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^" >&2
    false
}

############
#  assert  #  Compare actual vs expected string; fail if mismatch
############
#
# Compares string (default: $output) against the given string argument.
# By default we do an exact-match comparison against $output, but there
# are two different ways to invoke us, each with an optional description:
#
#      xpect               "EXPECT" [DESCRIPTION]
#      xpect "RESULT" "OP" "EXPECT" [DESCRIPTION]
#
# The first form (one or two arguments) does an exact-match comparison
# of "$output" against "EXPECT". The second (three or four args) compares
# the first parameter against EXPECT, using the given OPerator. If present,
# DESCRIPTION will be displayed on test failure.
#
# Examples:
#
#   xpect "this is exactly what we expect"
#   xpect "${lines[0]}" =~ "^abc"  "first line begins with abc"
#
function assert() {
    local actual_string="$output"
    local operator='=='
    local expect_string="$1"
    local testname="$2"

    case "${#*}" in
    0) die "Internal error: 'assert' requires one or more arguments" ;;
    1 | 2) ;;
    3 | 4)
        actual_string="$1"
        operator="$2"
        expect_string="$3"
        testname="$4"
        ;;
    *) die "Internal error: too many arguments to 'assert'" ;;
    esac

    # Comparisons.
    # Special case: there is no !~ operator, so fake it via '! x =~ y'
    local not=
    local actual_op="$operator"
    if [[ $operator == '!~' ]]; then
        not='!'
        actual_op='=~'
    fi
    if [[ $operator == '=' || $operator == '==' ]]; then
        # Special case: we can't use '=' or '==' inside [[ ... ]] because
        # the right-hand side is treated as a pattern... and '[xy]' will
        # not compare literally. There seems to be no way to turn that off.
        if [ "$actual_string" = "$expect_string" ]; then
            return
        fi
    elif [[ $operator == '!=' ]]; then
        # Same special case as above
        if [ "$actual_string" != "$expect_string" ]; then
            return
        fi
    else
        if eval "[[ $not \$actual_string $actual_op \$expect_string ]]"; then
            return
        elif [ $? -gt 1 ]; then
            die "Internal error: could not process 'actual' $operator 'expect'"
        fi
    fi

    # Test has failed. Get a descriptive test name.
    if [ -z "$testname" ]; then
        testname="${MOST_RECENT_BUILDAH_COMMAND:-[no test name given]}"
    fi

    # Display optimization: the typical case for 'expect' is an
    # exact match ('='), but there are also '=~' or '!~' or '-ge'
    # and the like. Omit the '=' but show the others; and always
    # align subsequent output lines for ease of comparison.
    local op=''
    local ws=''
    if [ "$operator" != '==' ]; then
        op="$operator "
        ws=$(printf "%*s" ${#op} "")
    fi

    # This is a multi-line message, which may in turn contain multi-line
    # output, so let's format it ourself, readably
    local actual_split
    IFS=$'\n' read -rd '' -a actual_split <<<"$actual_string" || true
    printf "#/vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv\n" >&2
    printf "#|     FAIL: %s\n" "$testname" >&2
    printf "#| expected: %s'%s'\n" "$op" "$expect_string" >&2
    printf "#|   actual: %s'%s'\n" "$ws" "${actual_split[0]}" >&2
    local line
    for line in "${actual_split[@]:1}"; do
        printf "#|         > %s'%s'\n" "$ws" "$line" >&2
    done
    printf "#\\^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n" >&2
    false
}

#################
#  assert_json  #  Compare actual json vs expected string; fail if mismatch
#################
# assert_json works like assert except that it accepts one extra parameter,
# the jq query string.
# There are two different ways to invoke us, each with an optional description:
#
#      xpect               "JQ_QUERY"      "EXPECT" [DESCRIPTION]
#      xpect "JSON_STRING" "JQ_QUERY" "OP" "EXPECT" [DESCRIPTION]
# Important this function will overwrite $output, so if you need to use the value
# more than once you need to safe it in another variable.
function assert_json() {
    local actual_json="$output"
    local operator='=='
    local jq_query="$1"
    local expect_string="$2"
    local testname="$3"

    case "${#*}" in
    0 | 1) die "Internal error: 'assert_json' requires two or more arguments" ;;
    2 | 3) ;;
    4 | 5)
        actual_json="$1"
        jq_query="$2"
        operator="$3"
        expect_string="$4"
        testname="$5"
        ;;
    *) die "Internal error: too many arguments to 'assert_json'" ;;
    esac
    run_helper jq -r "$jq_query" <<<"$actual_json"
    assert "$output" "$operator" "$expect_string" "$testname"
}
