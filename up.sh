source ./env/bin/activate
export DICELANG_DATASTORE="/home/$USER/.atropos-vars"
export DICELANG_CORE_EDITORS="/home/$USER/.atropos-vars/editors"
export ATROPOS_TOKEN_FILE="/home/$USER/.atropos-vars/token"
export ATROPOS_ID_FILE="/home/$USER/.atropos-vars/id"
while true; do
  python3 atropos.py
  echo "Atropos stopped with exit code $?. Respawning in 3..."
  sleep 1
  echo "2..."
  sleep 1
  echo "1..."
  sleep 1
done


