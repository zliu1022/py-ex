# ladder test

IFS="\n"
no=1
while read line
    do
        if [[ $line =~ "loadsgf" ]]
        then
            cmd=$line"\nshowboard\nfinal_status_list ladder\n"
        fi
        if [[ $line =~ "move" ]]
        then
            move=`echo ${line: 5}`
        fi
        if [[ $line =~ "result" ]]
        then
            exp_ret=`echo ${line: 7}`
            ret=`echo -e "$cmd" | ./leelaz -g -w ~/go/weights/1.gz 2>&1 | grep $move`
            echo $ret | grep $exp_ret > /dev/null
            [[ $? == 0 ]] && result="OK"
            echo "No." $no
            echo "actually:" $ret
            echo "expect  :" $exp_ret
            echo "compare: " $result
            echo
            no=`echo "$no+1"|bc`
        fi
    done <$1
