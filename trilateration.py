import ast

# 1) Known anchor positions in 3D but we'll just use the (x,y).
#    anchor1 = (0.1, 0.1, 0.1)
#    anchor2 = (0.1, 42.8, 0.02)
#    anchor3 = (59, 0.1, 0.02)
# For 2D trilateration, we take:


def trilateration_2d(d1, d2, d3, anchors):
    """
    Given distances d1, d2, d3 to anchors in 2D (x1,y1), (x2,y2), (x3,y3),
    solve the 2D trilateration equations to find (x, y).

    We'll use a standard approach by subtracting equations:
       (x - x1)^2 + (y - y1)^2 = d1^2
       (x - x2)^2 + (y - y2)^2 = d2^2
       (x - x3)^2 + (y - y3)^2 = d3^2
    """
    (x1, y1) = anchors[0]
    (x2, y2) = anchors[1]
    (x3, y3) = anchors[2]

    # Convert distances to squared form for convenience
    r1_sq = d1**2
    r2_sq = d2**2
    r3_sq = d3**2

    # We'll create two linear equations by subtracting:
    # EqA: (Eq1 - Eq2)
    # EqB: (Eq1 - Eq3)

    # Eq1: (x - x1)^2 + (y - y1)^2 = r1_sq
    # Eq2: (x - x2)^2 + (y - y2)^2 = r2_sq
    # Sub(Eq1-Eq2):
    #    x^2 - 2x x1 + x1^2 + y^2 - 2y y1 + y1^2  -  ( x^2 - 2x x2 + x2^2 + y^2 - 2y y2 + y2^2 ) = r1_sq - r2_sq
    #
    # This simplifies to a linear form: A1*x + B1*y + C1 = 0
    # We'll solve similarly for EqA (from Eq1-Eq2) and EqB (from Eq1-Eq3).

    A1 = 2*(x2 - x1)
    B1 = 2*(y2 - y1)
    C1 = (x1**2 - x2**2) + (y1**2 - y2**2) + (r2_sq - r1_sq)

    A2 = 2*(x3 - x1)
    B2 = 2*(y3 - y1)
    C2 = (x1**2 - x3**2) + (y1**2 - y3**2) + (r3_sq - r1_sq)

    # Now we have a system:
    # A1*x + B1*y + C1 = 0
    # A2*x + B2*y + C2 = 0
    #
    # We can solve using standard 2x2 linear algebra (Cramer's rule):
    det = A1*B2 - A2*B1
    if abs(det) < 1e-10:
        # Degenerate case - anchors might be collinear or distances impossible
        # Return None or some fallback
        return None

    # Solve for x, y
    x = (B2*(-C1) - B1*(-C2)) / det
    y = (A1*(-C2) - A2*(-C1)) / det

    return (x, y)

def calculateListOfPoints(filepath = "", anchors = []):
    """
    Reads each line from an input file named 'distances.txt'.
    Each line is a dictionary-like string, for example:
        {'TagName':'Tag1', 'Anchor1':10.55, 'Anchor2':37.81, 'Anchor3':51.31}
    Then calculates the 2D position of that tag using trilateration.
    """
    
    xyPoints = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # skip empty lines

            # 2) Parse the dictionary-like string
            #    e.g. "{'TagName':'Tag1', 'Anchor1':10.55, 'Anchor2':37.81, 'Anchor3':51.31}"
            row_data = ast.literal_eval(line)  # convert string to dict

            # Extract distances
            d1 = float(row_data["Anchor1"])
            d2 = float(row_data["Anchor2"])
            d3 = float(row_data["Anchor3"])
            tag_name = row_data["TagName"]

            # 3) Trilateration
            result = trilateration_2d(d1, d2, d3, anchors)
            if result is not(None):
                x_est, y_est = result
                #print(f"Tag={tag_name}: Position=({x_est:.2f}, {y_est:.2f})")
                xyPoints.append((x_est, y_est))

    return xyPoints
if __name__ == "__main__":
    input_file = "C:\\Users\\thano\\OneDrive - Αριστοτέλειο Πανεπιστήμιο Θεσσαλονίκης\\PhD Dissertation\\PositioningDataClassifier\\TStransporter.txt"
    anchors_2d = [
        (0.1, 0.1),    # Anchor1
        (0.1, 42.8),   # Anchor2
        (59.0, 0.1)    # Anchor3
    ]
    points = calculateListOfPoints(filepath=input_file, anchors = anchors_2d)
    print(points)
    print(len(points))