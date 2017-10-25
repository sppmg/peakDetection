#include<stdio.h>
#include<stdbool.h>

#define link_dataBlock_len 10
#define list_data_type unsigned long
#include"slist_dataStorage.h"

// void peak_detect(double *data, unsigned long dataLen, long flt_pd);

typedef struct Extrema_info {
    unsigned long max_i_len ;
    unsigned long *max_i ;
    unsigned long min_i_len ;
    unsigned long *min_i ;
    unsigned long rm_max_len ;
    unsigned long *rm_max ;
    unsigned long rm_min_len ;
    unsigned long *rm_min ;
} Extrema_info;

struct Filters {
    unsigned long pd ;
    unsigned char ph_num ; // : 2; // 0 ~ 2
    double *ph ;
    unsigned char th_num ;//: 2; // 0 ~ 4
    double *th ;
};

// mark removed extrema in filter ph. (inline to reduce source)
void filter_ph_mark_rm(List *rm_max, unsigned long i_max,
                              List *rm_min, unsigned long i_min){
    static unsigned long rm_min_last = -1,
                         rm_max_last = -1 ;
    if(rm_max_last != i_max){
        rm_max_last = i_max ;
        list_data_append(rm_max, rm_max_last) ;
    }
    if(rm_min_last != i_min){
        rm_min_last = i_min;
        list_data_append(rm_min, rm_min_last) ;
    }
}



Extrema_info peak_detect(double *data, unsigned long dataLen, struct Filters flt){
    List* rec_max = new_slist();
    List* rec_min = new_slist();
    
    long n = 0,
        preExtr_i = 0,
        blkEnd_i = flt.pd ;
    double preExtr_v = *(data) ;
    bool find_max = true ;

    // Determine first extrema is max or min
    int tmp_max_i = 0,tmp_min_i = 0;
    double tmp_max_v = *(data),tmp_min_v = *(data);
    for(int i = 0; i < flt.pd; ++i){
        if(*(data+i) > tmp_max_v){
            tmp_max_i = i ;
            tmp_max_v = *(data+i);
        }
        if(*(data+i) < tmp_min_v){
            tmp_min_i = i ;
            tmp_min_v = *(data+i);
        }
    }

    find_max = tmp_max_i < tmp_min_i ? true : false ;
    
    // Scan data
    while(n < dataLen){

        if( find_max ? *(data + n ) >= preExtr_v : *(data + n ) <= preExtr_v ){
            preExtr_i = n ;
            preExtr_v = *(data+n) ;
            n++ ;
        }else if( n >= preExtr_i + flt.pd ){
            // log peak
            list_data_append(find_max ? rec_max : rec_min, preExtr_i);
            n = preExtr_i ;
            // set find min
            find_max = ! find_max ;
        }else{
            n++ ;
        }
    }

    List *rm_max = new_slist() ;
    List *rm_min = new_slist() ;

    // filter for flt.ph (relatively height of peak and around local minimum)

    if(flt.ph_num > 0){
        // chech max_num >= 1
    
        unsigned long i_max = 0, i_min = 0 ;
        double extrDiff_lowSide, extrDiff_highSide ;

        // if first extrema is max, check extrDiff_highSide and shift i_max
        if(list_data_get(rec_max, 0) < list_data_get(rec_min, 0)){
            extrDiff_highSide = data[list_data_get(rec_max, i_max)] - data[list_data_get(rec_min, i_min)];
            
            
            if(extrDiff_highSide < flt.ph[0]){
                filter_ph_mark_rm(rm_max, 0, rm_min, 0);
            }
            if(flt.ph_num == 2)
                if(extrDiff_highSide > flt.ph[1])
                    filter_ph_mark_rm(rm_max, 0, rm_min, 0);
            i_max = 1 ;
            i_min = 0 ;
        }

        unsigned long orig_max_i_len = list_data_total(rec_max) ;

        unsigned long i_max_len = list_data_get(rec_max, orig_max_i_len -1) <
                            list_data_get(rec_min, list_data_total(rec_min) -1) ?
                            orig_max_i_len : orig_max_i_len -1 ;

        while(i_max < i_max_len){
            extrDiff_lowSide = data[list_data_get(rec_max, i_max)] - data[list_data_get(rec_min, i_min)];
            extrDiff_highSide = data[list_data_get(rec_max, i_max)] - data[list_data_get(rec_min, i_min + 1)];
            
            if(extrDiff_lowSide < flt.ph[0])
                filter_ph_mark_rm(rm_max, i_max, rm_min, i_min);
            if(extrDiff_highSide < flt.ph[0])
                filter_ph_mark_rm(rm_max, i_max, rm_min, i_min);

            // extrDiff > ph max
            if(flt.ph_num == 2){
                if(extrDiff_lowSide > flt.ph[1])
                    filter_ph_mark_rm(rm_max, i_max, rm_min, i_min);
                if(extrDiff_highSide > flt.ph[1])
                    filter_ph_mark_rm(rm_max, i_max, rm_min, i_min);
            }
            ++i_max;
            ++i_min;
        }

        // if last extrema is max, check extrDiff_lowSide
        if(i_max == i_max_len){
            extrDiff_lowSide = data[list_data_get(rec_max, i_max)] - data[list_data_get(rec_min, i_min)] ;
//             extrDiff_highSide = list_data_get(rec_max, i_max) - list_data_get(rec_min, i_min + 1);

            if(extrDiff_lowSide < flt.ph[0])
                filter_ph_mark_rm(rm_max, i_max, rm_min, i_min);
            if(flt.ph_num == 2)
                if(extrDiff_lowSide > flt.ph[1])
                    filter_ph_mark_rm(rm_max, i_max, rm_min, i_min);
        }
    } // end filter for ph



    // finish filters, export list to return type.
    
    Extrema_info extrema_info = {
        .max_i_len = 0 ,
        .max_i = NULL ,
        .min_i_len = 0 ,
        .min_i = NULL ,
        .rm_max_len = 0 ,
        .rm_max = NULL ,
        .rm_min_len = 0 ,
        .rm_min = NULL 
    };
    
    if(flt.ph_num > 0){ //|| flt.th_num > 0
        list_data_type *rm_max_arr;
        unsigned long rm_max_total_data;
        list_to_array(rm_max, &rm_max_arr, &rm_max_total_data);

        list_data_type *rm_min_arr;
        unsigned long rm_min_total_data;
        list_to_array(rm_min, &rm_min_arr, &rm_min_total_data);


        extrema_info.rm_max_len = rm_max_total_data ;
        extrema_info.rm_max = rm_max_arr ;
        extrema_info.rm_min_len = rm_min_total_data ;
        extrema_info.rm_min = rm_min_arr ;

        // remove marked extrema
        // Here use [i-1] because i is unsigned long, can't use i >= 0
        // the rm_* must be sorted seq.
        for(unsigned long i = rm_max_total_data ; i > 0; i--){
            unsigned long rm_idx = rm_max_arr[i-1];
            rm_max_arr[i-1] = list_data_get(rec_max, rm_idx);
            list_data_rm(rec_max, rm_idx);
        }
        for(unsigned long i = rm_min_total_data ; i > 0; i--){
            unsigned long rm_idx = rm_min_arr[i-1];
            rm_min_arr[i-1] = list_data_get(rec_min, rm_idx);
            list_data_rm(rec_min, rm_idx);
        }
        

    }
    
    list_data_type *max_arr;
    unsigned long max_total_data;
    list_to_array(rec_max, &max_arr, &max_total_data);

    list_data_type *min_arr;
    unsigned long min_total_data;
    list_to_array(rec_min, &min_arr, &min_total_data);
    
    
    extrema_info.max_i_len = max_total_data ;
    extrema_info.max_i = max_arr;
    extrema_info.min_i_len = min_total_data ;
    extrema_info.min_i = min_arr ;
    



    list_free(rec_max) ;
    list_free(rec_min) ;
    
    list_free(rm_max) ;
    list_free(rm_min) ;
    
    return extrema_info ;
}

int main(){
    struct Filters flt = {.pd = 5, .ph_num = 1, .th_num = 0} ;
    double a[] = {3.3} ;
    flt.ph = a ;
//     double data[] = { 2,4,5,6,1,25,6};
    double data[] = {1, 1, 1.1, 1, 0.9, 1, 1, 1.1, 1, 0.9, 1, 1.1, 1, 1, 0.9, 1, 1, 1.1, 1, 1, 1, 1, 1.1, 0.9, 1, 1.1, 1, 1, 0.9, 1, 1.1, 1, 1, 1.1, 1, 0.8, 0.9, 1, 1.2, 0.9, 1, 1, 1.1, 1.2, 1, 1.5, 1, 3, 2, 5, 3, 2, 1, 1, 1, 0.9, 1, 1, 3, 2.6, 4, 3, 3.2, 2, 1, 1, 0.8, 4, 4, 2, 2.5, 1, 1, 1} ;
    Extrema_info extrema_info = peak_detect(data, sizeof(data)/sizeof(data[0]), flt);
    
    for(int i = 0; i < extrema_info.max_i_len; i++)
        printf("max[%d] = %u\n",i ,extrema_info.max_i[i]);
    for(int i = 0; i < extrema_info.min_i_len; i++)
        printf("min[%d] = %u\n",i ,extrema_info.min_i[i]);
    for(int i = 0; i < extrema_info.rm_max_len; i++)
        printf("rm_max[%d] = %u\n",i ,extrema_info.rm_max[i]);
    for(int i = 0; i < extrema_info.rm_min_len; i++)
        printf("rm_min[%d] = %u\n",i ,extrema_info.rm_min[i]);
    return 0;
}



