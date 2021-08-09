
def get_min_path(pred, dest):
    if dest is None:
        return None
    path = []
    crawl = dest
    path.append(crawl)

    while pred[crawl] != -1:
        path.append(pred[crawl])
        crawl = pred[crawl]
    path.reverse()
    return path


def bfs(src, graph):
    visited = {}
    pred = {}
    dist = {}
    for v in graph:
        visited[v] = False
        pred[v] = -1
        dist[v] = float('inf')
    queue = []  # Initialize a queue

    visited[src] = True
    dist[src] = 0
    queue.append(src)

    while len(queue) != 0:
        u = queue[0]
        queue.pop(0)
        for i in graph[u]:
            if not visited[i]:
                visited[i] = True
                dist[i] = dist[u] + 1
                pred[i] = u
                queue.append(i)

    return pred, dist

