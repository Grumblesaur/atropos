source ./env/bin/activate
export ATROPOS_CONFIG="/home/$USER/.atropos-vars"
export DICELANG_CORE_EDITORS="$ATROPOS_CONFIG/editors"
export ATROPOS_TOKEN_FILE="$ATROPOS_CONFIG/token"
export ATROPOS_ID_FILE="$ATROPOS_CONFIG/id"
export DJANGO_ALLOW_ASYNC_UNSAFE="true"
./build-readme.sh
while true; do
  python3 atropos.py
  echo "Atropos stopped with exit code $?. Respawning in 3..."
  sleep 1
  echo "2..."
  sleep 1
  echo "1..."
  sleep 1
done


