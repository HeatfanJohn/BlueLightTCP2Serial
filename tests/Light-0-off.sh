#nc -N localhost 1000 < ./Light-0-off.hex
{ cat 0-off.hex; sleep 1; } | nc -N localhost 1000
