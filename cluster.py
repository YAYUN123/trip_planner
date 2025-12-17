import numpy as np


# ---------------------- 核心函数：计算两点经纬度的距离（Haversine公式） ----------------------
def haversine_distance(lat1, lon1, lat2, lon2):
    """
    计算两个经纬度点之间的球面距离（单位：米）
    :param lat1: 点1纬度
    :param lon1: 点1经度
    :param lat2: 点2纬度
    :param lon2: 点2经度
    :return: 两点间距离（米）
    """
    # 地球半径（米）
    R = 6371000
    # 转弧度
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)

    # 纬度差、经度差
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine公式
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    distance = R * c
    return distance


# ---------------------- 构建距离矩阵 ----------------------
def build_distance_matrix(points):
    """
    构建n个点的距离矩阵（n×n）
    :param points: 经纬度列表，格式[[lon1, lat1], [lon2, lat2], ...]
    :return: 距离矩阵（二维数组）
    """
    n = len(points)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        lon1, lat1 = points[i]
        for j in range(i + 1, n):
            lon2, lat2 = points[j]
            dist = haversine_distance(lat1, lon1, lat2, lon2)
            dist_matrix[i][j] = dist
            dist_matrix[j][i] = dist
    return dist_matrix


# ---------------------- 贪心聚类：每组最多3个点，组内距离最近 ----------------------
def greedy_cluster(points, max_group_size=3):
    """
    贪心聚类算法：
    1. 从未分组的点中选一个点作为种子
    2. 找该点最近的k个点（k=max_group_size-1），组成一组
    3. 重复直到所有点分组完成
    :param points: 经纬度列表
    :param max_group_size: 每组最大数量（默认3）
    :return: 聚类结果（列表的列表，每个子列表是一组的点索引）
    """
    n = len(points)
    if n == 0:
        return []

    # 构建距离矩阵
    dist_matrix = build_distance_matrix(points)
    # 记录点是否已分组
    is_assigned = [False] * n
    clusters = []

    while not all(is_assigned):
        # 选第一个未分组的点作为种子
        seed = is_assigned.index(False)
        # 找种子到所有未分组点的距离
        unassigned_indices = [i for i in range(n) if not is_assigned[i]]
        dist_to_seed = [(i, dist_matrix[seed][i]) for i in unassigned_indices]
        # 按距离升序排序
        dist_to_seed.sort(key=lambda x: x[1])
        # 取前max_group_size个点组成组
        group = [x[0] for x in dist_to_seed[:max_group_size]]
        # 标记为已分组
        for idx in group:
            is_assigned[idx] = True
        # 添加到聚类结果
        clusters.append(group)

    return clusters