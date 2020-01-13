# match script
RESIGN=5
THREAD=2
GAMES=10

#player 1
CMD1=/Users/zliu/go/leela-zero/leelaz-dual
WEIGHT_1=/Users/zliu/go/weights/5x64/35.gz
PLAYOUT_1=1500

#player 2
CLOUD_IP=104.198.49.150
CMD2="ssh -i /Users/zliu/outline zliu1022@$CLOUD_IP /home/zliu1022/go/leelaz-dual"

WEIGHT_2=/home/zliu1022/go/OZ13.gz
START_KOMI=90
KOMI_STEP=5
PLAYOUT_2=43200

:<<!
WEIGHT_2=/home/zliu1022/go/OZ05.gz
START_KOMI=55
WEIGHT_2=/home/zliu1022/go/OZ06.gz
START_KOMI=60
WEIGHT_2=/home/zliu1022/go/OZ07.gz
START_KOMI=60
WEIGHT_2=/home/zliu1022/go/OZ08.gz
START_KOMI=70
WEIGHT_2=/home/zliu1022/go/OZ11.gz
START_KOMI=80
WEIGHT_2=/home/zliu1022/go/OZ10.gz
START_KOMI=85
WEIGHT_2=/home/zliu1022/go/OZ09.gz
START_KOMI=80
WEIGHT_2=/home/zliu1022/go/OZ12.gz
START_KOMI=80
WEIGHT_2=/home/zliu1022/go/OZ14.gz
START_KOMI=80
WEIGHT_2=/home/zliu1022/go/OZ15.gz
START_KOMI=80
!

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
    BLACK="$CMD1 -g --noponder --timemanage off -t$THREAD -r$RESIGN -w $WEIGHT_1 -p$PLAYOUT_1"
    WHITE="$CMD2 -g --noponder --timemanage off -t$THREAD -r$RESIGN -w $WEIGHT_2 -p$PLAYOUT_2"
    SGFNAME="$W_NAME1"-p"$PLAYOUT_1"_v_"$W_NAME2"-p"$PLAYOUT_2"-"$GAMES"
    PARA="-verbose -auto -games $GAMES -alternate -size 19 -komi 7.5 -sgffile $SGFNAME -time 7200m"
    ;;
"handicap")
    #BLACK="$CMD1 -g --noponder --timemanage off -t$THREAD -r$RESIGN -w $WEIGHT_1 -p$PLAYOUT_1"
    #WHITE="$CMD2 -g --noponder --timemanage off -t$THREAD -r$RESIGN -w $WEIGHT_2 -p$PLAYOUT_2 --komi $START_KOMI --kmrate 0.65 --kmstep $KOMI_STEP"
    #SGFNAME="$W_NAME1"-p"$PLAYOUT_1"-h4_v_"$W_NAME2"-p"$PLAYOUT_2"-"$GAMES"
    BLACK="java -jar gogui-client.jar 192.168.1.136 8801"
    WHITE="$CMD2 -g --noponder --timemanage off -t$THREAD -r$RESIGN -w $WEIGHT_2 -p$PLAYOUT_2 --komi $START_KOMI --kmrate 0.65 --kmstep $KOMI_STEP"
    SGFNAME=zen7-s9000-h4_v_"$W_NAME2"-p"$PLAYOUT_2"-"$GAMES"
    PARA="-openings /Users/zliu/github/Webgo/sgf/handicap/h4/ -verbose -auto -games $GAMES -size 19 -komi 0 -sgffile $SGFNAME -time 7200m"
    ;;
*)
    echo "para error"
    exit
    ;;
esac

:<<!
echo "black player:"
echo $BLACK
echo
echo "white player:"
echo $WHITE
echo
echo "para:"
echo $PARA
!

java -jar gogui-twogtp.jar -black "$BLACK" -white "$WHITE" $PARA
#./match.sh handicap >&1 2>&1 | tee match-201911061550.log
