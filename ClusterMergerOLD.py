import math
import matplotlib.pyplot as plt

def euclidean_distance(p1, p2):
    """Compute Euclidean distance between points p1=(x1,y1) and p2=(x2,y2)."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def update_center(cluster):
    """Recalculate the center of a cluster based on all its points."""
    xs = [pt[0] for pt in cluster["points"]]
    ys = [pt[1] for pt in cluster["points"]]
    cluster["center"] = (sum(xs)/len(xs), sum(ys)/len(ys))

def merge_clusters(main_cluster_id, other_cluster_id, clusters):
    """
    Merge 'other_cluster_id' into 'main_cluster_id' and remove 'other_cluster_id' from 'clusters'.
    Steps:
      1) Move points from 'other_cluster_id' to 'main_cluster_id'.
      2) Update the center of 'main_cluster_id'.
      3) Redirect all clusters that flowed to 'other_cluster_id' so they now flow to 'main_cluster_id'.
      4) Let 'main_cluster_id' adopt the 'flow_to' of 'other_cluster_id', overwriting its own.
      5) Remove 'other_cluster_id' from 'clusters'.
    """
    main_cluster = clusters[main_cluster_id]
    other_cluster = clusters[other_cluster_id]

    # 1) Move points
    main_cluster["points"].extend(other_cluster["points"])
    
    # 2) Update center
    update_center(main_cluster)
    
    # 3) Redirect flows toward the old cluster to the main cluster
    for cid, clus in clusters.items():
        if cid != other_cluster_id and clus["flow_to"] == other_cluster_id:
            clus["flow_to"] = main_cluster_id

    # 4) Inherit the 'flow_to' from the other cluster
    #    This way, if other_cluster was going to e.g. cluster 6, now main_cluster points there.
    main_cluster["flow_to"] = other_cluster["flow_to"]

    # 5) Remove the old cluster
    del clusters[other_cluster_id]

def plot_clusters_with_flow(clusters):
    """
    Plots each cluster's center and draws an arrow to the cluster indicated by 'flow_to'.
    Clusters is a dictionary of the form:
    {
        cluster_id: {
            "id": cluster_id,
            "center": (x_center, y_center),
            "points": [(x1,y1), (x2,y2), ...],
            "flow_to": other_cluster_id or None
        },
        ...
    }
    """
    fig, ax = plt.subplots()

    # Plot each cluster's center
    for cid, cluster_data in clusters.items():
        center = cluster_data["center"]
        ax.scatter(center[0], center[1], label=f"Cluster {cid}")
        ax.text(center[0] + 0.1, center[1] + 0.1, f"ID={cid}", fontsize=9)

    # Draw arrows based on flow_to
    for cid, cluster_data in clusters.items():
        flow_target = cluster_data["flow_to"]
        if flow_target is not None and flow_target in clusters:
            source_center = cluster_data["center"]
            target_center = clusters[flow_target]["center"]
            # Draw an arrow from source cluster to target cluster
            ax.annotate(
                "",  # no text
                xy=target_center,
                xytext=source_center,
                arrowprops=dict(arrowstyle="->", lw=1.5),
            )

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("Clusters with Flow Arrows")
    ax.legend()
    plt.show()

def merge_all_within_threshold(clusters, threshold):
    """
    Continuously merges any two clusters whose centers are within the given threshold,
    until no more merges can be done in a single pass.
    """
    clearPass = True
    merged_something = True
    while merged_something:
        merged_something = False
        current_ids = sorted(clusters.keys())

        for i_index in range(len(current_ids)):
            cid_i = current_ids[i_index]
            if cid_i not in clusters:
                continue  # might have been removed in a previous merge

            for j_index in range(i_index+1, len(current_ids)):
                cid_j = current_ids[j_index]
                if cid_j not in clusters:
                    continue  # might have been removed in a previous merge

                dist = euclidean_distance(clusters[cid_i]["center"], clusters[cid_j]["center"])
                if dist < threshold:
                    clearPass = False
                    print(f"Merging cluster {cid_j} into cluster {cid_i} (distance={dist:.2f})")
                    merge_clusters(cid_i, cid_j, clusters)
                    merged_something = True
                    break
            if merged_something:
                # Start over, in case the newly merged cluster can merge with something else
                break

    return clusters, clearPass

if __name__ == "__main__":
    # Example dictionary of clusters
    clusters = {
        1: {
            "id": 1,
            "center": (1.0, 1.0),
            "points": [(1, 1)],
            "flow_to": 2
        },
        2: {
            "id": 2,
            "center": (2.0, 2.0),
            "points": [(2, 2), (2, 3)],
            "flow_to": 3
        },
        3: {
            "id": 3,
            "center": (5.0, 6.0),
            "points": [(5, 6)],
            "flow_to": 4
        },
        4: {
            "id": 4,
            "center": (2, 2),
            "points": [(2, 2), (2, 2)],
            "flow_to": 5
        },
        5: {
            "id": 5,
            "center": (9.0, 9.0),
            "points": [(9, 9)],
            "flow_to": 6
        },
        6: {
            "id": 6,
            "center": (2, 2),
            "points": [(1.5, 1.5)],
            "flow_to": None
        }
    }

    threshold = 2.0
    clusters2 = clusters.copy()
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
    plot_clusters_with_flow(clusters)
    plot_clusters_with_flow(clusters2)


