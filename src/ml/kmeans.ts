export function euclideanDistance(left: number[], right: number[]): number {
  let sum = 0
  for (let index = 0; index < left.length; index += 1) {
    sum += (left[index] - right[index]) ** 2
  }
  return Math.sqrt(sum)
}

function mean(points: number[][]): number[] {
  if (points.length === 0) return []
  const dimensionCount = points[0].length
  const centroid = new Array<number>(dimensionCount).fill(0)

  for (const point of points) {
    for (let dimension = 0; dimension < dimensionCount; dimension += 1) {
      centroid[dimension] += point[dimension]
    }
  }

  return centroid.map((total) => total / points.length)
}

function pickInitialCentroids(points: number[][], clusterCount: number): number[][] {
  const centroids: number[][] = [points[0]]
  const chosenIndexes = new Set<number>([0])

  while (centroids.length < clusterCount && centroids.length < points.length) {
    let farthestIndex = -1
    let farthestDistance = -1

    for (let index = 0; index < points.length; index += 1) {
      if (chosenIndexes.has(index)) continue
      const distanceToNearestCentroid = Math.min(
        ...centroids.map((centroid) => euclideanDistance(points[index], centroid)),
      )
      if (distanceToNearestCentroid > farthestDistance) {
        farthestDistance = distanceToNearestCentroid
        farthestIndex = index
      }
    }

    if (farthestIndex === -1) break
    centroids.push(points[farthestIndex])
    chosenIndexes.add(farthestIndex)
  }

  return centroids
}

export function kMeansCluster(points: number[][], clusterCount: number, maxIterations = 100): number[] {
  const labels = new Array<number>(points.length).fill(0)

  if (points.length === 0) return labels

  const effectiveCount = Math.max(1, Math.min(clusterCount, points.length))
  if (effectiveCount === 1) return labels

  let centroids = pickInitialCentroids(points, effectiveCount)

  for (let iteration = 0; iteration < maxIterations; iteration += 1) {
    for (let index = 0; index < points.length; index += 1) {
      let nearest = 0
      let nearestDistance = Number.POSITIVE_INFINITY
      centroids.forEach((centroid, centroidIndex) => {
        const distance = euclideanDistance(points[index], centroid)
        if (distance < nearestDistance) {
          nearestDistance = distance
          nearest = centroidIndex
        }
      })
      labels[index] = nearest
    }

    const nextCentroids: number[][] = []
    let converged = true
    for (let centroidIndex = 0; centroidIndex < centroids.length; centroidIndex += 1) {
      const clusterPoints = points.filter((_, index) => labels[index] === centroidIndex)
      const nextCentroid = clusterPoints.length > 0 ? mean(clusterPoints) : centroids[centroidIndex]
      if (euclideanDistance(nextCentroid, centroids[centroidIndex]) > 1e-9) {
        converged = false
      }
      nextCentroids.push(nextCentroid)
    }

    centroids = nextCentroids
    if (converged) break
  }

  return labels
}
