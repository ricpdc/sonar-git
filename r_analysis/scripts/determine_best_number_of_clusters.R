
library(pamk)
library(cluster)

#Methods for determine best number of clusters in K-means

#1. Look for a bend or elbow in the sum of squared error (SSE) scree plot

mydata <- dataset_only_data
wss <- (nrow(mydata)-1)*sum(apply(mydata,2,var))
for (i in 2:15) wss[i] <- sum(kmeans(mydata,
                                     centers=i)$withinss)
plot(1:15, wss, type="b", xlab="Number of Clusters",
     ylab="Within groups sum of squares")


#2. partitioning around medoids to estimate the number of clusters using the pamk function in the fpc package.
pamk.best <- pamk(dataset1)
cat("number of clusters estimated by optimum average silhouette width:", pamk.best$nc, "\n")
plot(pam(dataset_only_data, pamk.best$nc))



#3 Calinsky criterion: Another approach to diagnosing how many clusters suit the data. In this case we try 1 to 10 groups.
require(vegan)
fit <- cascadeKM(scale(dataset_only_data, center = TRUE,  scale = TRUE), 1, 10, iter = 1000)
plot(fit, sortg = TRUE, grpmts.plot = TRUE)
calinski.best <- as.numeric(which.max(fit$results[2,]))
cat("Calinski criterion optimal number of clusters:", calinski.best, "\n")


#4. Determine the optimal model and number of clusters according to the Bayesian Information Criterion for expectation-maximization, initialized by hierarchical clustering for parameterized Gaussian mixture models

# See http://www.jstatsoft.org/v18/i06/paper  # http://www.stat.washington.edu/research/reports/2006/tr504.pdf

# library(mclust)
# # Run the function to see how many clusters it finds to be optimal, set it to search for at least 1 model and up 20.
# d_clust <- Mclust(as.matrix(dataset_only_data), G=1:20)
# m.best <- dim(d_clust$z)[2]
# cat("model-based optimal number of clusters:", m.best, "\n")
# # 4 clusters
# plot(d_clust)


#5. Affinity propagation (AP) clustering, see http://dx.doi.org/10.1126/science.1136800
library(apcluster)
d.apclus <- apcluster(negDistMat(r=2), d)
cat("affinity propogation optimal number of clusters:", length(d.apclus@clusters), "\n")
heatmap(d.apclus)
plot(d.apclus, d)
