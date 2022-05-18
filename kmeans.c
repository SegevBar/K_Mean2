#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

typedef struct 
{
    int vector_count;
    double* vectors_sum;
    double* centroid;
} Cluster;

/*Prototypes*/
void calcCluster(double* vector, Cluster* clusters, int k, int dim);
double calcDistance(double* vector1, double* vector2, int dim);
int updateCentroids(Cluster* clusters, int k, int dim);


int main(int argc, char *argv[]){
    int hasMaxIter = 1;
    int max_iter = 0;
    int k = 1;
    FILE *ifp = NULL;
    FILE *ofp = NULL;
    int c;
    char ch;
    double value;
    int N = 0;
    int dim = 1;
    Cluster* clusters;
    double* currVector = NULL;
    int has_converged = 0;
    int cnt = 0;
    int i = 0;
    int j = 0;
    
    /*check input for enough params*/
    if ((argc < 4) || (argc > 5)) {
        printf("Invalid Input!\n");
        exit(1);
    } else {
        if (argc == 4) {
            hasMaxIter = 0;
        }
    }
    
    /*find max_iter*/
    if (hasMaxIter == 0) {  /*check if max_iter is default or param*/
        max_iter = 200;
    } else {
        if ((atoi(argv[2]) <= 0) || (strchr(argv[2], '.') != NULL)) {
            printf("Invalid Input!\n");
            exit(1);
        }
        max_iter = atoi(argv[2]);
    }  
    
    /*open input file*/
    ifp = fopen(argv[2 + hasMaxIter], "r");
    if (ifp == NULL) {
        printf("Invalid Input!\n");
        exit(1);
    }

    /*find vector dimensions*/
    while ((c = fgetc(ifp)) != 10) {  /*run until end of line*/
        if (c == 44) {  /*if c == "," increment dimension*/
            dim++; 
        }
    }
    rewind(ifp);

    /*find N*/
    while ((c = fgetc(ifp)) != EOF) {  /*run until end of file*/
        if(c == 10) { /*if (c == "\n") increment N*/
            N++;
        }
    }
    rewind(ifp);

    /*find k and check if valid*/ 
    k = atoi(argv[1]);
    if ((strchr(argv[1], '.') != NULL) || (N <= k) || (k <= 1)) {
        printf("Invalid Input!\n");
        exit(1);
    }
   
    /*Init k clusters*/
    clusters = (Cluster*)calloc(k,sizeof(Cluster));
    
    for (i = 0; i < k; i++){
        clusters[i].vector_count = 0; /*init cluster vector counter*/

        /*init sum of vectors in cluster*/ 
        clusters[i].vectors_sum = (double*)calloc(dim, sizeof(double));
        if (clusters[i].vectors_sum == NULL) {
            printf("An Error Has Occurred\n");
            exit(1);
        }

        /*init centroid to i'th vectors*/
        clusters[i].centroid = (double*)calloc(dim, sizeof(double));
        if (clusters[i].centroid == NULL) {
            printf("An Error Has Occurred\n");
            exit(1);
        }
        for (j = 0; j < dim; j++){
           fscanf(ifp, "%lf%c", &value, &ch);
           clusters[i].centroid[j] = value;
        }
    }
    rewind(ifp);

    /*main loop*/
    cnt = 0;
    while ((cnt < max_iter) && (!has_converged)) {

        /*find current vector cluster*/
        for (i = 0; i < N; i++) {
            currVector = (double*)calloc(dim, sizeof(double));
            if (currVector == NULL) {
                printf("An Error Has Occurred\n");
                exit(1);
            }
            for (j = 0; j < dim; j++){
                fscanf(ifp, "%lf%c", &value, &ch);
                currVector[j] = value;
            }
            calcCluster(currVector, clusters, k, dim);
            free(currVector);
        }
        
        /*update centroids*/
        has_converged = updateCentroids(clusters, k, dim);
        
        rewind(ifp);
        
        for(i = 0; i < k; i++){
            clusters[i].vector_count = 0;
            for(j = 0; j < dim; j++){
                clusters[i].vectors_sum[j] = 0;
            }
        }
        cnt++;
    }
    fclose(ifp);

    /*write to output file*/
    ofp = fopen(argv[3 + hasMaxIter], "w");
    if (ofp == NULL) {
        printf("Invalid Input!\n");
        exit(1);
    }
    for (i = 0; i < k; i++) {
        for (j = 0; j < dim-1; j++){
            fprintf(ofp, "%.4f%c", clusters[i].centroid[j], ',');
        }
        fprintf(ofp, "%.4f%c", clusters[i].centroid[dim-1], '\n');
    }
    fclose(ofp);
    
    /*free clusters memory*/
    for(i = 0; i < k; i++){
        free(clusters[i].centroid);
        free(clusters[i].vectors_sum);
    }
    free(clusters);

    return 0;
}

void calcCluster(double* vector, Cluster* clusters, int k, int dim) {
    double min_distance = -1.0;
    int closest_cluster = -1;
    double distance;
    int i = 0;
    int j = 0;

    /*find closest cluster to current vector*/
    for (i = 0; i < k; i++) {
        distance = calcDistance(vector, clusters[i].centroid, dim);
        if ((distance < min_distance) || (min_distance < 0)) {
            min_distance = distance; 
            closest_cluster = i;
        }
    }
    
    /*update closest cluster*/
    clusters[closest_cluster].vector_count++; 
    for (j = 0; j < dim; j++) {
        clusters[closest_cluster].vectors_sum[j] += vector[j];
    }
}

double calcDistance(double* vector1, double* vector2, int dim) {
    double sum = 0.0;
    int j = 0;

    for (j = 0; j < dim; j++) {
        sum += (vector1[j]-vector2[j])*(vector1[j]-vector2[j]);
    } 
    return sum;
}

int updateCentroids(Cluster* clusters, int k, int dim) {
    double epsilon = 0.001;
    int i = 0;
    int j = 0;
    int has_converged = 1;
    double* new_centroid = NULL;
    double dist = 0;

    /*calculate new centroid*/
    for (i = 0; i < k; i++) {
        new_centroid = (double*)calloc(dim, sizeof(double));
        if (new_centroid == NULL) {
            printf("An Error Has Occurred\n");
            exit(1);
        }
        for (j = 0; j < dim; j++) {
            new_centroid[j] = (clusters[i].vectors_sum[j]/clusters[i].vector_count);
        }
        dist = sqrt(calcDistance(clusters[i].centroid, new_centroid, dim));

        /*check if convergence did not accured*/
        if (dist >= epsilon) {
            has_converged = 0;
        }

        /*update centroid*/
        memcpy(clusters[i].centroid, new_centroid, sizeof(double)*dim);

        free(new_centroid);
    }
    return has_converged;
}
