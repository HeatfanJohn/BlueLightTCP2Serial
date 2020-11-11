{ printf '\x02\x18\x18\x02\x18\x18'$1'\x0d'; sleep 1; } | nc -N localhost 1000
