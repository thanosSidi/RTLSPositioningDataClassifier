from .ClusterMerger import plot_clusters_with_flow, merge_all_within_threshold, classesToClusterDictionary
from .PointClassifier import classify_points_latest_only

if __name__ == "__main__":
    data_points = [
        (1, 2), (2, 2), (5, 5), (5, 6),(5, 6),(5, 6),(5, 6), (2.2, 2.9), (2.2, 2.9), (2.2, 2.9),
        (10, 10),(10, 10),(10, 10),(10, 10), (11, 12), (9, 9), (2, 3), (2.2, 2.9), (2.2, 2.9), (2.2, 2.9), (2.2, 2.9), 
        (5, 6),(5, 6),(5, 6),(5, 6), (5, 6),(5, 6),(5, 6),(5, 6), (1,2), (1,2), (1,2), (1,2), (1,2), (1,2), (5, 6),(5, 6),(5, 6),(5, 6), (1,2), (1,2), (1,2), (1,2), (1,2)
    ]

    distance_threshold = 2.0

    results = classify_points_latest_only(data_points, distance_threshold)
    clusters = classesToClusterDictionary(results)
    """
    for i, cluster in enumerate(results):
        print(f"Cluster {i+1}:")
        print(f"  Center: {cluster['center']}")
        print(f"  Points: {cluster['points']}")
        print()
    print(clusters)
    plot_clusters_with_flow(clusters)
    """

    threshold = 2.0
    clusters2 = clusters.copy()
    
    plot_clusters_with_flow(clusters)
    clearPass = False
    passNo = 1
    while clearPass == False:
        clusters2, clearPass = merge_all_within_threshold(clusters2, threshold)
        print("============= PASS No", passNo ,"=============")
        
        for cid, clus in clusters2.items():
            print(f"Cluster {cid}:")
            print(f"  Center: {clus['center']}")
            print(f"  Points: {clus['points']}")
            print(f"  Flows to: {clus['flow_to']}")
        print("=============                =============")
        passNo += 1

    print("\n---- Clusters after merges ----")
    for cid, clus in clusters2.items():
        print(f"Cluster {cid}:")
        print(f"  Center: {clus['center']}")
        print(f"  Points: {clus['points']}")
        print(f"  Flows to: {clus['flow_to']}")

    # Finally, visualize
    plot_clusters_with_flow(clusters2)
