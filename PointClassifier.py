import math
__all__ = ["classify_points_latest_only"]

def euclidean_distance(p1, p2):
    """Return the Euclidean distance between two points p1=(x1,y1), p2=(x2,y2)."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
def drop_clusters_with_low_number_of_points(clusters, minLength):
    newClusters = []
    for i,cls in enumerate(clusters):
        if len(cls["points"]) >= minLength:
            newClusters.append(cls)
    return newClusters
def classify_points_latest_only(points, threshold):
    """
    Clusters (x,y) points by checking each new point only against
    the most recently created cluster.
    
    Algorithm:
    1. First point → first cluster (center = that point).
    2. For each subsequent point:
       - Compare distance to the center of the 'latest' cluster only.
       - If distance < threshold, add point to that cluster and update center.
       - Otherwise, create a new cluster with this point as its center.

    Returns a list of clusters, each cluster being a dict with:
        {
          "center": (cx, cy),
          "points": [(x1, y1), (x2, y2), ...]
        }
    """
    if not points:
        return []

    # Initialize the first cluster with the first point
    clusters = [{
        "center": points[0],
        "points": [points[0]]
    }]

    def update_center(cluster):
        xs = [pt[0] for pt in cluster["points"]]
        ys = [pt[1] for pt in cluster["points"]]
        # New center is the average of x and y coordinates
        cluster["center"] = (sum(xs)/len(xs), sum(ys)/len(ys))

    # Go through the rest of the points
    for point in points[1:]:
        # Always compare with the 'latest' (most recently created) cluster
        latest_cluster = clusters[-1]
        dist = euclidean_distance(point, latest_cluster["center"])

        if dist < threshold:
            # Add this point to the latest cluster
            latest_cluster["points"].append(point)
            update_center(latest_cluster)
        else:
            # Create a brand new cluster
            new_cluster = {
                "center": point,
                "points": [point]
            }
            clusters.append(new_cluster)

    return clusters

if __name__ == "__main__":
    # Example usage:
    data_points = [
        (1, 2), (2, 2), (5, 5), (5, 6),(5, 6),(5, 6),(5, 6), (2.2, 2.9), (2.2, 2.9), (2.2, 2.9),
        (10, 10),(10, 10),(10, 10),(10, 10), (11, 12), (9, 9), (2, 3), (2.2, 2.9), (2.2, 2.9), (2.2, 2.9), (2.2, 2.9), 
        (5, 6),(5, 6),(5, 6),(5, 6), (5, 6),(5, 6),(5, 6),(5, 6), (1,2), (1,2), (1,2), (1,2), (1,2), (1,2), (5, 6),(5, 6),(5, 6),(5, 6), (1,2), (1,2), (1,2), (1,2), (1,2)
    ]
    distance_threshold = 2.0

    results = classify_points_latest_only(data_points, distance_threshold)
    results = drop_clusters_with_low_number_of_points(results, 4)
    clusters = {  }

    for i, cluster in enumerate(results):
        temp_dict = { "id": i+1,
            "center": cluster['center'],
            "points": cluster['points'],
            "flow_to": [i+2]}
        if (i+1) == len(results) :
            temp_dict["flow_to"] = []
        clusters[i+1] = temp_dict
        print(f"Cluster {i+1}:")
        print(f"  Center: {cluster['center']}")
        print(f"  Points: {cluster['points']}")
        print()
    print(clusters)