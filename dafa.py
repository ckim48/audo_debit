dx = [-1,1,0,0]
dy = [0,0,-1,1]

def dfs(y0,x0,cnt):
    global maxcnt
    if cnt > maxcnt:
        maxcnt = cnt
    if cnt == 26: # cannot exceed 26, the number of alphabets
        return 26

    for dd in range(4):
        y1 = y0 + dy[dd]
        x1 = x0 + dx[dd]
        if 0<=y1<N and 0<=x1<M and visited[ord(board[y1][x1])-65] == 0:
            visited[ord(board[y1][x1])-65] = 1
            dfs(y1,x1,cnt+1)
            visited[ord(board[y1][x1])-65] = 0


N, M = map(int,input().split())
board = [list(input()) for _ in range(N)]
maxcnt = 1
visited = [0]*26
visited[ord(board[0][0])-65] = 1
dfs(0,0,1)
print(maxcnt)