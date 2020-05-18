path="./helpfiles/"
ext=".md"
declare -a files=(
  "quickstart"
  "commands"
)

cat $path/atropos.md > README.md
for f in "${files[@]}"; do
  cat "$path/$f$ext" >> README.md
done

