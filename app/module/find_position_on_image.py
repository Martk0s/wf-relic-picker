import cv2
import numpy as np
from module.utils import resource_path


# find an object on image
def best_match_coordinates(
    reference_image_path, search_image, search_image_path=None, debug_window=False
):
    # Load the reference image (object you want to find)
    reference_image = cv2.imread(resource_path(reference_image_path))

    # Load the image in which you want to find the object (for debuging)
    if search_image_path:
        search_image = cv2.imread(search_image_path)

    # Convert images to grayscale
    reference_gray = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)
    search_gray = cv2.cvtColor(search_image, cv2.COLOR_BGR2GRAY)

    # Use the SIFT (Scale-Invariant Feature Transform) feature detector and descriptor
    sift = cv2.SIFT_create()

    # Find keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(reference_gray, None)
    kp2, des2 = sift.detectAndCompute(search_gray, None)

    # Use the BFMatcher (Brute-Force Matcher) to find the best matches between the descriptors
    bf = cv2.BFMatcher()

    # Match descriptors
    matches = bf.knnMatch(des1, des2, k=2)

    # Apply ratio test
    good_matches = []
    for m, n in matches:
        if m.distance < 0.4 * n.distance:
            good_matches.append(m)

    try:
        # Extract coordinates of the best match in search_image
        best_match_index = good_matches[
            0
        ].trainIdx  # Index of the best match in the training (search_image) keypoints
    except IndexError:
        raise ValueError("Position of {thing_to_find} was not found")

    best_match_coordinates = kp2[best_match_index].pt  # Coordinates of the best match

    if debug_window:
        # Print the coordinates of the best match
        print(best_match_coordinates)

        # Draw the matches on the images
        img_matches = cv2.drawMatches(
            reference_image,
            kp1,
            search_image,
            kp2,
            good_matches,
            None,
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
        )

        # Set the desired width of the window
        window_width = 2000

        # Calculate the corresponding height to maintain the aspect ratio
        aspect_ratio = img_matches.shape[1] / img_matches.shape[0]
        window_height = int(window_width / aspect_ratio)

        # Resize the window before displaying the result
        cv2.namedWindow("Matches", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Matches", window_width, window_height)

        # Display the result
        cv2.imshow("Matches", img_matches)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return best_match_coordinates


def kmeans_v2(
    reference_image_path, search_image, search_image_path=None, debug_window=False
):
    # Load the reference image (object you want to find)
    reference_image = cv2.imread(resource_path(reference_image_path))

    # Load the image in which you want to find the object (for debugging)
    if search_image_path:
        search_image = cv2.imread(search_image_path)

    # Convert images to grayscale
    try:
        reference_gray = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)
    except cv2.error:
        raise ValueError("Model files not found.")
    search_gray = cv2.cvtColor(search_image, cv2.COLOR_BGR2GRAY)

    # Use the SIFT (Scale-Invariant Feature Transform) feature detector and descriptor
    sift = cv2.SIFT_create()

    # Find keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(reference_gray, None)
    kp2, des2 = sift.detectAndCompute(search_gray, None)

    # Use the BFMatcher (Brute-Force Matcher) to find the best matches between the descriptors
    bf = cv2.BFMatcher()

    # Match descriptors
    matches = bf.knnMatch(des1, des2, k=2)

    # Apply ratio test
    good_matches = []
    for m, n in matches:
        if m.distance < 0.5 * n.distance:
            good_matches.append(m)

    # Extract matched keypoints
    matched_kp = [kp2[m.trainIdx].pt for m in good_matches]

    # Convert matched keypoints to NumPy array
    matched_kp = np.array(matched_kp, dtype=np.float32)

    # Raise ValueError when not found
    if not len(matched_kp):
        raise ValueError("Unable to locate {thing_to_find}.")

    # Calculate clustering using K-means
    num_cluster = 2
    if len(matched_kp) < num_cluster:
        num_cluster = len(matched_kp)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 0.1)
    _, labels, centers = cv2.kmeans(
        matched_kp, num_cluster, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
    )

    # Find the label with the most occurrences
    unique, counts = np.unique(labels, return_counts=True)
    max_label = unique[np.argmax(counts)]

    # Get the center of the cluster with the highest density
    center_x, center_y = centers[max_label]

    if debug_window:
        # Draw a red circle at the center of the cluster
        cv2.circle(search_image, (int(center_x), int(center_y)), 10, (50, 50, 255), 5)

        # Draw the matches on the images
        print("Centers of clusters:", (center_x, center_y))
        img_matches = cv2.drawMatches(
            reference_image,
            kp1,
            search_image,
            kp2,
            good_matches,
            None,
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
        )

        # Set the desired width of the window
        window_width = 2000

        # Calculate the corresponding height to maintain the aspect ratio
        aspect_ratio = img_matches.shape[1] / img_matches.shape[0]
        window_height = int(window_width / aspect_ratio)

        # Resize the window before displaying the result
        cv2.namedWindow("Preview", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Preview", window_width, window_height)

        # Display the result
        cv2.imshow("Preview", img_matches)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return center_x, center_y
