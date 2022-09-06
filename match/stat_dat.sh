fn=$1
count=0
while read line
do
    count=`expr $count + 1`
    if [ $count -gt 16 ]; then
        # 0 W+R W+R W+R 0 - 386 54.5 54.9 0 0 0
        array=(${line// / })
        len=${array[6]}
:<<!
        for var in ${array[@]}
        do
           echo $var
        done
!
        if [ $len -lt $2 ]; then
            #echo $line
            echo ${array[0]} ${array[1]} $len
        fi
    fi
done < $fn
