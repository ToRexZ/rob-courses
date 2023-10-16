import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt


# Import images
rgb_raw = o3d.io.read_image("images/rgb.png")
depth_raw = o3d.io.read_image("images/depth.png")

# Exercise 1: Generate a coloured point cloud from the images
# Lets start by generating an RGBD image
rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(rgb_raw, depth_raw)

# Now lets render the image using numpy
plt.subplot(1, 2, 1)
plt.title("Grayscale image")
plt.imshow(rgbd.color)
plt.subplot(1, 2, 2)
plt.title("Depth image")
plt.imshow(rgbd.depth)
plt.show()

# Now lets convert the RGBD image to a point cloud

# Create pinhole camera intrinsics
intrinsic_matrix = [
    [572.4114, 0.0, 325.2611],
    [0.0, 573.57043, 242.04899],
    [0.0, 0.0, 1.0],
]

intrinsic = o3d.camera.PinholeCameraIntrinsic()
intrinsic.set_intrinsics(
    # rgbd.color.width,  # width
    # rgbd.color.height,  # height
    rgbd.width,
    rgbd.height,
    intrinsic_matrix[0][0],  # fx
    intrinsic_matrix[1][1],  # fy
    intrinsic_matrix[0][2],  # cx
    intrinsic_matrix[1][2],  # cy
)

pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd, intrinsic)

# Flip it, otherwise the pointcloud will be upside down
pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
o3d.visualization.draw_geometries([pcd], zoom=0.5)
