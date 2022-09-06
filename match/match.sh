# no handicap
#CMD=/Users/zliu/go/leela-zero/leelaz-dual
CMD=/Users/zliu/go/leela-zero/leelaz-20210825
#CMD=/Users/zliu/github/leela-zero/src/leelaz
RESIGN=10
THREAD=1
GAMES=$3

#weight 1
WEIGHT_1=/Users/zliu/go/weights/4x32/4b32f.gz
#WEIGHT_1=/Users/zliu/Downloads/4b32f/all/152000
PLAYOUT_1=300

#weight 2
WEIGHT_2=/Users/zliu/Downloads/4b32f/all/$2
PLAYOUT_2=300

START_KOMI=80
KOMI_STEP=5

get_name_from_path(){
    temp=${1##*/}
    name=${temp%.*}
    echo $name
    return $?
}
W_NAME1=`echo $(get_name_from_path $WEIGHT_1)`
W_NAME2=`echo $(get_name_from_path $WEIGHT_2)`

case $1 in
"normal")
    # normal game
    BLACK="$CMD -g --noponder --timemanage off -t$THREAD -r$RESIGN -w $WEIGHT_1 -p$PLAYOUT_1"
    WHITE="$CMD -g --noponder --timemanage off -t$THREAD -r$RESIGN -w $WEIGHT_2 -p$PLAYOUT_2 --ladder 1 --ladder-dep 9"
    SGFNAME="$W_NAME1"-p"$PLAYOUT_1"_v_"$W_NAME2"-p"$PLAYOUT_2"-"$GAMES"
    PARA="-verbose -auto -games $GAMES -alternate -size 19 -komi 7.5 -sgffile $SGFNAME -time 7200m"
    ;;
"handicap")
    # handicap game
    #BLACK="$CMD -g --noponder --timemanage off -t$THREAD -r$RESIGN -w $WEIGHT_1 -p$PLAYOUT_1"
    BLACK="java -jar gogui-client.jar 192.168.1.136 8801"
    #WHITE="$CMD -g --noponder --timemanage off -t$THREAD -r$RESIGN -w $WEIGHT_2 -p$PLAYOUT_2 --komi $START_KOMI --kmrate 0.65 --kmstep $KOMI_STEP"
    WHITE="ssh -i /Users/zliu/outline zliu1022@35.223.182.248 /home/zliu1022/go/leelaz-dual -g --noponder --timemanage off -t$THREAD -r$RESIGN -w /home/zliu1022/go/OZ14.gz -p$PLAYOUT_2 --komi $START_KOMI --kmrate 0.65 --kmstep $KOMI_STEP"
    #SGFNAME="$W_NAME1"-p"$PLAYOUT_1"-h4_v_"$W_NAME2"-p"$PLAYOUT_2"-"$GAMES"
    SGFNAME=zen7-s1500-h4_v_"$W_NAME2"-p"$PLAYOUT_2"-"$GAMES"
    PARA="-openings /Users/zliu/github/Webgo/sgf/handicap/h4/ -verbose -auto -games $GAMES -size 19 -komi 0 -sgffile $SGFNAME -time 7200m"
    ;;
*)
    echo "para error"
    exit
    ;;
esac

:<<!
echo black "$BLACK"
echo white "$WHITE"
echo para $PARA
!

java -jar gogui-twogtp.jar -black "$BLACK" -white "$WHITE" $PARA

#./match.sh normal > 4b32f-p300_v_246000-p300-200.log 2>&1
#python ~/github/py-ex/dat2htm/dat2stat.py 4b32f-p300_v_186000-p300-200.dat
#python ~/github/py-ex/draw/draw_match_rate.py 4b32f-p300_v_186000-p300-200.log
