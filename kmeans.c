#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#define PY_SSIZE_T_CLEAN
#include <Python.h>

typedef struct 
{
    int vector_count;
    double* vectors_sum;
    double* centroid;
} Cluster;

/*Prototypes*/
static PyObject *kmeans(int k, int max_iter, int dim_py, int N_py, PyObject *centroids_py, PyObject *vectors_py);
void calcCluster(double* vector, Cluster* clusters, int k, int dim);
double calcDistance(double* vector1, double* vector2, int dim);
int updateCentroids(Cluster* clusters, int k, int dim);
PyObject *cToPy(Cluster *clusters, int k, int dim, double **vectors, int N);
static PyObject *fit_capi(PyObject *self, PyObject *args);


int main(int argc, char *argv[]){
    return 0;
}


static PyObject *kmeans(int k, int max_iter, int dim_py, int N_py, PyObject *centroids_py, PyObject *vectors_py){
    int N = N_py;
    int dim = dim_py;
    Cluster* clusters;
    double *curr_vector;
    int has_converged = 0;
    int cnt = 0;
    int i = 0;
    int j = 0;

    /*convert k centroids from python to C*/
    cnt = 0;
    clusters = (Cluster *)calloc(k, sizeof(struct Cluster));
    if (clusters == NULL) {
        printf("An Error Has Occurred\n");
        exit(1);
    }
    
    for (i = 0; i < k; i++){
        clusters[i].centroid = (double *)calloc(dim, sizeof(double));
        if (clusters[i].centroid == NULL) {
            printf("An Error Has Occurred\n");
            exit(1);
        }

        memcpy(clusters[i].centroid, vectors[PyLong_AsLong(PyList_GetItem(centroids_locations, cnt))], sizeof(double) * dim); 
        
        clusters[i].s = 0;
        clusters[i].vectors_sum = (double *)calloc(dim, sizeof(double));
        if (clusters[i].vectors_sum == NULL){
            printf("An Error Has Occurred\n");
            exit(1);
        }
        cnt++;
    }

    /*main loop*/
    cnt = 0;
    while ((cnt < max_iter) && (!has_converged)) {

        /*find current vector cluster*/
        for (i = 0; i < N; i++) {
            curr_vector = (double*)calloc(dim, sizeof(*curr_vector[i]));
            if (currVector == NULL) {
                printf("An Error Has Occurred\n");
                exit(1);
            }
            for (j = 0; j < dim; j++){
                curr_vector[j] = PyFloat_AsDouble(PyList_GetItem(vectors_py, cnt));
                cnt++;
            }
            calcCluster(curr_vector, clusters, k, dim);
            free(curr_vector);
        }
        
        /*update centroids*/
        has_converged = updateCentroids(clusters, k, dim);
        
        /*reset*/
        for(i = 0; i < k; i++){
            clusters[i].s = 0;
            for(j = 0; j < dim; j++){
                clusters[i].vectors_sum[j] = 0;
            }
        }
        cnt++;
    }

    return cToPy(clusters, k, dim, vectors, N);
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
    clusters[closest_cluster].s++; 
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
            new_centroid[j] = (clusters[i].vectors_sum[j]/clusters[i].s);
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

/*convert centroids from C to python*/
PyObject *cToPy(Cluster *clusters, int k, int dim, double **vectors, int N){
    PyObject *clusters_py;
    int i = 0;
    int j = 0;
    PyObject *value;

    clusters_py = PyList_New(k);
    for (i = 0; i < k; i++){
        PyObject *curr_vector;
        curr_vector = PyList_New(dim);
        for (j = 0; j < dim; j++){
            value = Py_BuildValue("d", clusters[i].centroid[j]);
            PyList_SetItem(curr_vector, j, value);
        }
        /*add PyObject centroid to PyList clusters*/
        PyList_SetItem(clusters_py, i, curr_vector);
    }
    /*free clusters memory*/
    for (i = 0; i < k; i++){
        free(clusters[i].centroid);
        free(clusters[i].vectors_sum);
    }
    free(clusters);
    
    return clusters_py;
}


/*fit() function. gets arguments from python to kmeans function*/
static PyObject *fit_capi(PyObject *self, PyObject *args){
    int k;
    int max_iter;
    int dim_py;
    int N_py;
    PyObject *centroids_locations;
    PyObject *vectors_py;

    if (!(PyArg_ParseTuple(args, "iiiiOO", &k, &max_iter, &dim_py, &N_py, &centroids_locations, &vectors_py))){
        return NULL;
    }
    if (!PyList_Check(centroids_locations) || !PyList_Check(vectors_py)){
        return NULL;
    }

    return Py_BuildValue("O", kmeans(k, max_iter, dim_py, N_py, centroids_locations, vectors_py));
}

/*building mykmeanssp module*/
static PyMethodDef kmeansMethods[] = {
    {"fit",
     (PyCFunction)fit_capi,
     METH_VARARGS,
     PyDoc_STR("kmeans algorithem")},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef moduledef =
    {
        PyModuleDef_HEAD_INIT,
        "mykmeanssp",
        NULL,
        -1,
        kmeansMethods};

PyMODINIT_FUNC
PyInit_mykmeanssp(void)
{
    PyObject *m;
    m = PyModule_Create(&moduledef);
    if (!m){
        return NULL;
    }
    return m;
}
