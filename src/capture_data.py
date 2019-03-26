#!/usr/bin/env python


from time import time
import rospy
import numpy as np
import pyrealsense2 as rs
import sys
from std_srvs.srv import Empty, EmptyResponse
import os
from scipy.misc import imsave

DEFAULT_SAVE = os.path.join(os.path.expanduser('~'), 'Pictures')

def capture(msg):
    frames_raw = pipe.wait_for_frames()
    timestamp = int(time())

    # TODO: For the point cloud, I believe we need to use the non-aligned frame

    pc = rs.pointcloud()
    pc.map_to(frames_raw.get_color_frame())
    points = pc.calculate(frames_raw.get_depth_frame())

    # TODO: For other purposes, need aligned? check on this
    frames = rs.align(rs.stream.color).process(frames_raw)

    color = frames.get_color_frame()
    depth = frames.get_depth_frame()

    color_array = np.asanyarray(color.get_data())
    depth_array = np.asanyarray(rs.colorizer().colorize(depth).get_data())

    imsave(os.path.join(save_loc, '{}_color.png'.format(timestamp)), color_array)
    imsave(os.path.join(save_loc, '{}_depth.png'.format(timestamp)), depth_array)
    points.export_to_ply(os.path.join(save_loc, '{}_points.ply'.format(timestamp)), frames_raw.get_color_frame())

    print('Saved data!')
    return EmptyResponse()

if __name__ == "__main__":

    rospy.init_node('realsense_capture')

    save_loc = rospy.get_param('/realsense_capture/location') or DEFAULT_SAVE
    if not os.path.isdir(save_loc):
        print('{} is not a valid directory!'.format(save_loc))
        sys.exit(1)
    else:
        print('Files will be saved to {}'.format(save_loc))

    pipe = rs.pipeline()
    pipe.start()
    print('Image feed initialized')

    service = rospy.Service('realsense/capture', Empty, capture)
    print('Capture service initialized')
    rate = rospy.Rate(20)

    while not rospy.is_shutdown():
        rate.sleep()

    pipe.stop()
    print('Cleaned up!')