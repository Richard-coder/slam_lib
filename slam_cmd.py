import argparse
import os
import sys
import subprocess
import signal

docker_cmd = "docker run --env=\"DISPLAY\" " \
                "--net=host --runtime=nvidia " \
                "--volume=\"$HOME/.Xauthority:/root/.Xauthority:rw\" " \
                 "--env=\"QT_X11_NO_MITSHM=1\"" \
                " -v /tmp/.X11-unix:/tmp/.X11-unix:ro -it --rm --name slam_from_qt " \
                "-v /home:/out_home {} " \
                " /bin/bash -c \"/bin/bash /root/run_{}.sh {}\""


# "vins_mono", "svo", "vins_mono", "svo",
slam_types = ["全部", "基于滤波器", "特征法", "直接法", "多传感器融合"]
type2algos = {"全部": ["vins_mono", "dso", "svo", "okvis", "orb_slam", "lsd_slam", "rovio", "basalt", "ice_ba", "msckf"],
              "基于滤波器": [],
              "特征法": ["orb_slam"],
              "直接法": ["lsd_slam", "dso"],
              "多传感器融合": ["vins_mono", "svo", "okvis", "rovio", "basalt", "ice_ba", "msckf"]}

algo2image = {algo:"ros_slam_image:19-7-22" for algo in ["dso", "svo", "okvis", "orb_slam", "lsd_slam", "rovio", "ice_ba"]}
algo2image.update({algo:"ros_slam_image:kinetic_19-7-26" for algo in ["vins_mono", "msckf"]})
algo2image.update({algo:"no_ros_slam:basalt-v1" for algo in ["basalt"]})

algo2datasets = {"vins_mono":["euroc", "eth-aslcla", "ar_box"],
                 "dso":["monoVO"],
                 "svo":["airground_rig"],
                 "okvis":["euroc"],
                 "orb_slam":["tum", "kitti", "euroc"],
                 "lsd_slam":["lsd_room"],
                 "rovio":["euroc"],
                 "basalt":["euroc", "tumvi"],
                 "ice_ba":["euroc"],
                 "msckf":["euroc"]}


def main(config):

    if config.algo_dataset in type2algos["全部"]:
        print("available datasets for {}: {}".format(config.algo_dataset, algo2datasets[config.algo_dataset]))
        return
    if config.algo is None:
        print("Please specify an algorithm")
        return
    if config.dataset is None or not config.dataset in algo2datasets[config.algo]:
        print("Please specify an dataset in {}".format(algo2datasets[config.algo]))
        return
    print("Running slam, you can press ctrl+c to stop it")
    subprocess.Popen(docker_cmd.format(algo2image[config.algo], config.algo, config.dataset), shell=True)

    def signal_handler(sig, frame):
        print('You pressed Ctrl+C! Stopping running...')
        subprocess.Popen("docker stop --time 1 slam_from_qt", shell=True)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C')
    signal.pause()



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--algo', type=str, choices=type2algos["全部"], help='algorithm to run')
    parser.add_argument('--dataset', type=str,
                        help='dataset to run, you\'d better use \'--algo_dataset\' to see which datasets are available')
    parser.add_argument('--algo_dataset', type=str, choices=type2algos["全部"],
                        help='pass algorithm to see which datasets are available for it')
    config = parser.parse_args()

    main(config)

