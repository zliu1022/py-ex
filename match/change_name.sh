dir=/Users/zliu/Downloads/4b32f/all
for f in $dir/*; do
    if [ -f "$f" ]; then
        basename="${f##*/}";
        tmpname=${basename#*-model-}
        lastname=${tmpname%.txt*}
        newname=$dir"/"$lastname
        echo 'change' $f 'to' $newname
        sudo chmod 666 $f
        mv $f $newname
    fi
done

