import math
import matplotlib.pyplot as plt

__all__ = ["plot_clusters_with_flow", "merge_all_within_threshold"]

def euclidean_distance(p1, p2):
    """Compute Euclidean distance between points p1=(x1,y1) and p2=(x2,y2)"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def update_center(cluster):
    """Recalculate the center of a cluster based on all its points"""
    xs = [pt[0] for pt in cluster["points"]]
    ys = [pt[1] for pt in cluster["points"]]
    if len(xs) > 0:
        cluster["center"] = (sum(xs)/len(xs), sum(ys)/len(ys))
    else:
        cluster["center"] = (0, 0)

def merge_clusters(main_cluster_id, other_cluster_id, clusters):
    """
    Merge 'other_cluster_id' into 'main_cluster_id'.
      1) Move points from 'other_cluster_id' → 'main_cluster_id'.
      2) Update the center of 'main_cluster_id'.
      3) In every cluster's flow_to list, replace 'other_cluster_id' with 'main_cluster_id'.
      4) Combine the flow_to lists of main & other (union) and store that in main_cluster.
      5) Remove 'other_cluster_id' from 'clusters'.
    """
    main_cluster = clusters[main_cluster_id]
    other_cluster = clusters[other_cluster_id]

    # 1) Move points
    main_cluster["points"].extend(other_cluster["points"])

    # 2) Update center
    update_center(main_cluster)

    # 3) Redirect any references to 'other_cluster_id' in flow_to lists
    for cid, clus in clusters.items():
        if cid == other_cluster_id:
            continue  # We'll remove it soon anyway
        new_flow_to = []
        for target in clus["flow_to"]:
            if target == other_cluster_id:
                new_flow_to.append(main_cluster_id)
            else:
                new_flow_to.append(target)

        # Remove duplicates if you like, e.g. convert to set, then back to list
        clus["flow_to"] = list(set(new_flow_to))

    # 4) Combine flow_to lists (union of sets to avoid duplicates)
    combined_flow = set(main_cluster["flow_to"]) | set(other_cluster["flow_to"])
    # Remove self if it exists
    if main_cluster_id in combined_flow:
        combined_flow.remove(main_cluster_id)
    main_cluster["flow_to"] = list(combined_flow)

    # 5) Finally remove the other cluster
    del clusters[other_cluster_id]

def plot_clusters_with_flow(clusters, ax=None, image= None, pixelsPerMeter = None):
    """
    Plots each cluster's center and draws arrows based on its flow_to list.
    'flow_to' is a list of IDs of clusters to which the current cluster flows.
    """
    if ax == None:
        fig, ax = plt.subplots()
        
        # Plot each cluster center
        for cid, cluster_data in clusters.items():
            cx, cy = cluster_data["center"]
            ax.scatter(cx, cy, label=f"Cluster {cid}")
            ax.text(cx + 0.1, cy + 0.1, f"ID={cid}", fontsize=9)

        # Draw arrows
        for cid, cluster_data in clusters.items():
            source_center = cluster_data["center"]
            for flow_target in cluster_data["flow_to"]:
                if flow_target in clusters:
                    target_center = clusters[flow_target]["center"]
                    ax.annotate(
                        "",
                        xy=target_center,    # arrow head
                        xytext=source_center, 
                        arrowprops=dict(
                            arrowstyle="->", 
                            lw=1.5,
                            connectionstyle="arc3,rad=0.2"
                        )
                    )

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title("Clusters (Multiple flow targets)")
        ax.legend()
        plt.show()
    else:
        ax.clear()  # Clear old plot
        if image.any():
            height, width = image.shape[:2]
            ax.imshow(image, extent=[0, width/pixelsPerMeter, 0, height/pixelsPerMeter])
        for cid, cluster_data in clusters.items():
            cx, cy = cluster_data["center"]
            ax.scatter(cx, cy, label=f"Cluster {cid}")
            ax.text(cx + 0.1, cy + 0.1, f"ID={cid}", fontsize=9)

        # Draw arrows
        for cid, cluster_data in clusters.items():
            source_center = cluster_data["center"]
            for flow_target in cluster_data["flow_to"]:
                if flow_target in clusters:
                    target_center = clusters[flow_target]["center"]
                    ax.annotate(
                        "",
                        xy=target_center,    # arrow head
                        xytext=source_center, 
                        arrowprops=dict(
                            arrowstyle="->", 
                            lw=1.5,
                            connectionstyle="arc3,rad=0.2"
                        )
                    )
                    
        ax.set_title("Clusters (threshold-based merges)")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        #ax.legend()
        ax.figure.canvas.draw()
def merge_all_within_threshold(clusters, threshold):
    """
    Continuously merges any two clusters whose centers are within 'threshold',
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
                continue
            for j_index in range(i_index+1, len(current_ids)):
                cid_j = current_ids[j_index]
                if cid_j not in clusters:
                    continue

                dist = euclidean_distance(clusters[cid_i]["center"], 
                                          clusters[cid_j]["center"])
                if dist < threshold:
                    clearPass = False
                    print(f"Merging cluster {cid_j} into cluster {cid_i} (distance={dist:.2f})")
                    merge_clusters(cid_i, cid_j, clusters)
                    merged_something = True
                    break
            if merged_something:
                break
    return clusters, clearPass
def classesToClusterDictionary(classes):
    clusters = {  }
    for i, cluster in enumerate(classes):
        temp_dict = { "id": i+1,
            "center": cluster['center'],
            "points": cluster['points'],
            "flow_to": [i+2]}
        if (i+1) == len(classes) :
            temp_dict["flow_to"] = []
        clusters[i+1] = temp_dict
    return clusters
if __name__ == "__main__":
    # Example dictionary of clusters with 'flow_to' as lists
    clusters = {
        1: {
            "id": 1,
            "center": (1.0, 1.0),
            "points": [(1, 1)],
            # Suppose cluster 1 flows to clusters 2 and 3
            "flow_to": [2]
        },
        2: {
            "id": 2,
            "center": (2.0, 2.0),
            "points": [(2, 2), (2, 3)],
            # Suppose cluster 2 flows to cluster 4
            "flow_to": [3]
        },
        3: {
            "id": 3,
            "center": (5.0, 6.0),
            "points": [(5, 6)],
            "flow_to": [4]
        },
        4: {
            "id": 4,
            "center": (2.0, 2.0),
            "points": [(2, 2), (2, 2)],
            "flow_to": [5]
        },
        5: {
            "id": 5,
            "center": (9.0, 9.0),
            "points": [(9, 9)],
            "flow_to": [6]
        },
        6: {
            "id": 6,
            "center": (2.0, 2.0),
            "points": [(1.5, 1.5)],
            "flow_to": [7]
        },
        7: {
            "id": 7,
            "center": (5.0, 6.0),
            "points": [(5.5, 6.5)],
            "flow_to": [8]
        },
        8: {
            "id": 8,
            "center": (10, 10),
            "points": [(10, 10)],
            "flow_to": []
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
