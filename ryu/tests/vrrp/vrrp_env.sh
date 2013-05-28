#!/bin/bash
set -x

NS1="vrrp-rt1"
NS2="vrrp-rt2"

BR="vrrpbr"
VETH1="veth1"
VETH2="veth2"

BR_ADDR="172.16.10.100"
VETH1_ADDR="172.16.10.1"
VETH2_ADDR="172.16.10.2"
VR_ADDR="172.16.10.10"

VETH1_PEER="${VETH1}-br"
VETH2_PEER="${VETH2}-br"

_EXEC="sudo ip netns exec"
EXEC1="$_EXEC $NS1"
EXEC2="$_EXEC $NS2" 
WRAPPER="./tools/with_venv.sh"

function create_vrrp_env() {
    sudo ip netns add $NS1
    sudo ip netns exec $NS1 ip link set dev lo up
    sudo ip netns exec $NS1 ip addr add 127.0.0.1/8 dev lo
    sudo ip netns add $NS2
    sudo ip netns exec $NS2 ip link set dev lo up
    sudo ip netns exec $NS2 ip addr add 127.0.0.1/8 dev lo

    sudo brctl addbr $BR
    sudo ip link set dev $BR up
    sudo ip addr add $BR_ADDR/24 dev $BR

    sudo ip link add $VETH1 type veth peer name $VETH1_PEER
    sudo ip link set dev $VETH1 netns $NS1 up
    sudo ip netns exec $NS1 ip addr add $VETH1_ADDR/24 dev $VETH1
    sudo ip link set dev $VETH1_PEER up

    sudo ip link add $VETH2 type veth peer name $VETH2_PEER
    sudo ip link set dev $VETH2 netns $NS2 up
    sudo ip netns exec $NS2 ip addr add $VETH2_ADDR/24 dev $VETH2
    sudo ip link set dev $VETH2_PEER up

    sudo brctl addif $BR $VETH1_PEER
    sudo brctl addif $BR $VETH2_PEER
}

function delete_vrrp_env() {
    sudo brctl delif $BR $VETH1_PEER
    sudo brctl delif $BR $VETH2_PEER
    
    sudo ip netns exec $NS1 ip link delete $VETH1
    sudo ip netns exec $NS2 ip link delete $VETH2
    
    sudo ip link set dev $BR down
    sudo brctl delbr $BR
    
    sudo ip netns delete $NS1
    sudo ip netns delete $NS2    
}

function run_rt1() {
    $EXEC1 $WRAPPER \
        ./bin/ryu-manager --verbose \
        ./ryu/services/vrrp/manager.py \
        ./ryu/services/vrrp/rpc_manager.py
}

function run_rt2() {
    $EXEC2 $WRAPPER \
        ./bin/ryu-manager --verbose \
        ./ryu/services/vrrp/manager.py \
        ./ryu/services/vrrp/rpc_manager.py
}

function config_all() {
    $EXEC1 $WRAPPER \
        ./ryu/tests/vrrp/rpc_client.py \
            --method=config --vrid=16 --vripaddr=$VR_ADDR \
            --ifname=$VETH1 --ifipaddr=$VETH1_ADDR --priority=100

    $EXEC2 $WRAPPER \
        ./ryu/tests/vrrp/rpc_client.py \
            --method=config --vrid=16 --vripaddr=$VR_ADDR \
            --ifname=$VETH2 --ifipaddr=$VETH2_ADDR --priority=200
}

function list_all() {
    $EXEC1 $WRAPPER \
        ./ryu/tests/vrrp/rpc_client.py \
            --method=list --vrid=16

    $EXEC2 $WRAPPER \
        ./ryu/tests/vrrp/rpc_client.py \
            --method=list --vrid=16
}

function config_change() {
    $EXEC2 $WRAPPER \
        ./ryu/tests/vrrp/rpc_client.py \
            --method=config_change --vrid=16 --priority=50
}

case "$1" in
  create) create_vrrp_env;;
  delete) delete_vrrp_env;;
  run-rt1) run_rt1;;
  run-rt2) run_rt2;;
  config-all) config_all;;
  list-all) list_all;;
  config-change) config_change;;
esac

