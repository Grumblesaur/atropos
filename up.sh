source ./env/bin/activate
export DICELANG_DATASTORE="/home/$USER/.atropos_vars"
export ATROPOS_TOKEN_FILE="/home/$USER/.atropos_vars/token"
export ATROPOS_ID_FILE="/home/$USER/.atropos_vars/id"
while true; do
  python3 atropos.py
  echo "Atropos stopped with exit code $?. Respawning in 3..."
  sleep 1
  echo "2..."
  sleep 1
  echo "1..."
  sleep 1
done


