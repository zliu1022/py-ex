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
            cmd="\n$line\nshowboard\nladder 1"
            arr=($line)
            sgfpath=${arr[1]}
            movenum=${arr[2]}
            sgf=${sgfpath##*/}
            path=${sgfpath%/*}
            continue
        fi

        if [[ $line =~ "check" ]]
        then
            move=""
            type="" 
            exp_ret=""
            avoid=""
            avoid_list=""

            count=1
            for var in ${line[@]}
            do
               if [[ $count == 2 ]] 
               then
                  move=$var
               fi
               if [[ $count == 3 ]] 
               then
                  type=$var
               fi
               if [[ $count == 4 ]] 
               then
                  exp_ret=$var
               fi
               if [[ $count == 5 ]] 
               then
                  avoid=$var
               fi
               if [[ $count > 5 ]] 
               then
                  avoid_list=$avoid_list" "$var
               fi
               count=`echo "$count+1"|bc`
            done 
            #echo 'No.' $no
            #echo 'move      ' $move
            #echo 'type      ' $type 
            #echo 'result    ' $exp_ret
            #echo 'avoid     ' $avoid
            #echo 'avoid_list' $avoid_list

            echo -e "$cmd" | /Users/zliu/github/leela-zero/build/leelaz -g -w ~/go/weights/1.gz > ladder.test.out 2>&1
            ret=`grep "$move" ladder.test.out`
            #echo $ret
            echo "$ret" | grep "$exp_ret" > /dev/null
            if [[ $? == 0 ]] 
            then
                result=" OK"
            else
                result="ERR"
            fi

            avoid=`grep "avoid" ladder.test.out`
            #echo $avoid
            avoid_ret=""
            for avoid_pos in ${avoid_list[@]}
            do
                echo "$avoid" | grep "$avoid_pos" > /dev/null
                if [[ $? == 0 ]] 
                then
                    avoid_ret=$avoid_ret" OK"
                else
                    avoid_ret=$avoid_ret" ERR"
                fi
            done 


            echo "No."$no $result $avoid_ret $sgfpath $movenum

            if [[ $2 == "debug" ]]; then
                echo "actually:" $ret
                echo "expect  :" $exp_ret
                echo "avoid  :"  $avoid
                echo "expect avoid  :"  $avoid_list
                echo
            fi
            no=`echo "$no+1"|bc`
        fi
    done <$1
