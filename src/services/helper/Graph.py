import sys
from collections import defaultdict

from models.data.PipePathData import PipePathData
from models.data.PipePointData import PipePointData


def find_shortest_paths(start_point, point_data: list[PipePointData], path_data: list[PipePathData]):
    graph = defaultdict(list)
    for path in path_data:
        graph[path.startPointId].append((path.endPointId, path.id))
        graph[path.endPointId].append((path.startPointId, path.id))

    distances = {point.id: sys.maxsize for point in point_data}
    distances[start_point.id] = 0

    predecessors = {point.id: [] for point in point_data}

    unvisited = set(point_data)

    while unvisited:
        current_point = min(unvisited, key=lambda p: distances[p.id])
        unvisited.remove(current_point)

        for neighbor_id, edge_id in graph[current_point.id]:
            neighbor = next((point for point in point_data if point.id == neighbor_id), None)
            if neighbor and neighbor in unvisited:
                length = next((path.length for path in path_data if path.id == edge_id), None)
                if length is not None:
                    new_distance = distances[current_point.id] + length
                    if new_distance < distances[neighbor.id]:
                        distances[neighbor.id] = new_distance
                        predecessors[neighbor.id] = [(current_point.id, edge_id)]
                    elif new_distance == distances[neighbor.id]:
                        predecessors[neighbor.id].append((current_point.id, edge_id))

    shortest_paths = []

    for point in point_data:
        if (point != start_point) & (point.type == 'Connector'):
            shortest_path = []
            current_point_id = point.id
            while current_point_id != start_point.id:
                predecessor_id, edge_id = predecessors[current_point_id][0]
                shortest_path.append(edge_id)
                current_point_id = predecessor_id
            shortest_path.reverse()
            shortest_paths.append({
                'connector': point.id,
                'path': shortest_path,
                'distance': distances[point.id]
            })

    return shortest_paths

def find_critical_path(shortest_paths):
    return max(shortest_paths, key=lambda x: x['distance']) if shortest_paths else {}