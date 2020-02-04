source env/bin/activate
export DICELANG_DATASTORE='~/.atropos_vars'
while true; do
  python3 atropos.py
  echo "Atropos stopped with exit code $?. Respawning in 3..."
  sleep 1
  echo "2..."
  sleep 1
  echo "1..."
  sleep 1
done


