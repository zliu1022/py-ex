# ladder test

#IFS="\n"
no=1
while read line
    do
        first=`echo ${line: 0: 1}`
        if [[ $first == "#" ]]
        then
            continue
        fi
        if [[ $line =~ "loadsgf" ]]
        then
            cmd=$line"\nshowboard\nfinal_status_list ladder\n"
            arr=($line)
            sgfpath=${arr[1]}
            movenum=${arr[2]}
            sgf=${sgfpath##*/}
            path=${sgfpath%/*}
        fi
        if [[ $line =~ "pos" ]]
        then
            move=`echo ${line: 4}`
        fi

        if [[ $line =~ "escape" ]] || [[ $line =~ "capture" ]]
        then
            if [[ $line =~ "escape" ]]
            then
                exp_ret=`echo ${line: 7}`
            else
                exp_ret=`echo ${line: 8}`
            fi
            ret=`echo -e "$cmd" | /Users/zliu/github/leela-zero/build/leelaz -g -w ~/go/weights/1.gz 2>&1 | grep "$move"`
            echo "$ret" | grep "$exp_ret" > /dev/null
            if [[ $? == 0 ]] 
            then
                result=" OK"
            else
                result="ERR"
            fi
            echo "No."$no $result $sgfpath $movenum

            if [[ $2 == "debug" ]]; then
                echo "actually:" $ret
                echo "expect  :" $exp_ret
                echo
            fi
            no=`echo "$no+1"|bc`
        fi
    done <$1
