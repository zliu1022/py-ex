#./match.sh normal 296000 > /dev/null 2>&1
#./match.sh normal 456000 > /dev/null 2>&1

GAMES=400
sleeptime=600

dir=/Users/zliu/Downloads/4b32f/all
for f in $dir/*; do
    if [ -f "$f" ]; then
        basename="${f##*/}";
        echo `date "+%Y-%m-%d-%H-%M-%S"`
        echo "./match.sh normal $basename $GAMES > tmp.log 2>&1" 
        ./match.sh normal $basename $GAMES > tmp.log 2>&1
        python /Users/zliu/github/py-ex/dat2htm/dat2stat.py /Users/zliu/go/match/4b32f/4b32f-p300_v_$basename-p300-$GAMES.dat
        sleep $sleeptime
    fi
done

:<<!
for f in /Users/zliu/go/match/4b32f/4b32f-p300_v_*-p300-400.dat; do
    python /Users/zliu/github/py-ex/dat2htm/dat2stat.py $f
done
!


