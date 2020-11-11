#nc -N localhost 1000 -q 3 < ./0-on.hex
{ cat 0-on.hex; sleep 1; } | nc -N localhost 1000
