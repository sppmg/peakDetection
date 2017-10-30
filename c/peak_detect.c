#include<stdio.h>
#include<stdbool.h>

#define link_dataBlock_len 10
#define list_data_type unsigned long
#include"slist_dataStorage.h"
// #include"slist_dataStorage.h"

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
    unsigned char ph_num : 2; // 0 ~ 2
    double ph[2] ;
    unsigned char th_num : 3; // 0 ~ 4
    double th[4] ;
};

// mark removed extrema in filter ph. (use macro to reduce source)

// #define filter_ph_mark_rm(rm_max, i_max, rm_min, i_min) if(rm_max_last != i_max){rm_max_last = i_max ;list_data_append(rm_max, rm_max_last) ;}if(rm_min_last != i_min){rm_min_last = i_min;list_data_append(rm_min, rm_min_last) ;}
 
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



List* merge_lists_uniq(List* list_a, List* list_b){
    // arg include NULL.
    if(list_a == NULL){
        if(list_b == NULL)
            return NULL ;
        else
            return list_b ;
    }
    if(list_b == NULL){
        if(list_a == NULL)
            return NULL ;
        else
            return list_a ;
    }

    unsigned long a_len, b_len;
    a_len = list_data_total(list_a) ;
    b_len = list_data_total(list_b) ;
    List *merged_list = new_slist();

    unsigned long i_a = 0, i_b = 0, last = -1;
//     for(unsigned long i = 0; i < short_len; i++)
    while(i_a < a_len && i_b < b_len){
        unsigned long a = list_data_get(list_a, i_a),
                      b = list_data_get(list_b, i_b);
        printf("dbg: a = %lu, b = %lu",a,b);
        if(a < b && a != last){
            list_data_append(merged_list,a);
            last = a ;
            ++i_a ;
        }else if (a > b && b != last){
            list_data_append(merged_list,b);
            last = b ;
            ++i_b ;
        }else if(a != last){
            list_data_append(merged_list,a);
            ++i_a ;
            ++i_b ;
            last = a ;
        }
        printf(", app = %lu\n",last);
    }

    // 1 list end but another list not yet.
    if(i_a < a_len || i_b < b_len){
        unsigned long i, long_len;
        List *long_list = NULL ;

        if(i_a < a_len){
            i = i_a;
            long_list = list_a ;
            long_len = a_len ;
        }else{
            i = i_b;
            long_list = list_b ;
            long_len = b_len ;
        }
        printf("dbg: i_a = %lu, i_b = %lu, i = %lu\n",i_a,i_b, i);
        while(i < long_len){
            unsigned long val = list_data_get(long_list, i++) ;
            printf("dbg: i = %lu, val = %lu\n",i-1, val);
            if(val != last){
                list_data_append(merged_list, val);
                last = val ;
            }
        }
    }

    return merged_list ;

}


Extrema_info peak_detect(double *data, unsigned long dataLen, struct Filters flt){
    // prepare return variable
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
    
    // check filter setting
    if(flt.pd == 0)
        flt.pd = 1 ;
    if(flt.pd >= dataLen)
        return extrema_info ;
    if(flt.ph_num > 2)
        return extrema_info ;
    if(flt.th_num > 4 || flt.th_num == 3)
        return extrema_info ;
    
    List* rec_max = new_slist();
    List* rec_min = new_slist();

    // List rm_* will record index of rec_* till finish all filter and
    // export to extrema_info, then it's will transform to data index.
    List *rm_max = NULL ;
    List *rm_min = NULL ;
    
    unsigned long n = 0, preExtr_i = 0 ;
    double preExtr_v = *(data) ;
    bool find_max = true ;

    // Determine first extrema is max or min
    unsigned long tmp_max_i = 0,tmp_min_i = 0;
    double tmp_max_v = *(data),tmp_min_v = *(data);
    for(unsigned long i = 0; i < flt.pd; ++i){
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
    
    // Scan data, find extrema
    
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

    // ------------------------------------
    // Finish base extrema, start filters
    // ------------------------------------
    
    // filter for flt.ph (relatively height of peak and around local minimum)

    if(flt.ph_num > 0){
        // chech max_num >= 1

        List *rm_ph_max = new_slist() ;
        List *rm_ph_min = new_slist() ;
    
        unsigned long i_max = 0, i_min = 0 ;
        double extrDiff_lowSide, extrDiff_highSide ;

        unsigned long rm_min_last = -1, rm_max_last = -1 ;
        // if first extrema is max, check extrDiff_highSide and shift i_max
        if(list_data_get(rec_max, 0) < list_data_get(rec_min, 0)){
            extrDiff_highSide = data[list_data_get(rec_max, i_max)] - data[list_data_get(rec_min, i_min)];
            
            if(extrDiff_highSide < flt.ph[0]){
                filter_ph_mark_rm(rm_ph_max, 0, rm_ph_min, 0);
            }
            if(flt.ph_num == 2)
                if(extrDiff_highSide > flt.ph[1])
                    filter_ph_mark_rm(rm_ph_max, 0, rm_ph_min, 0);
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
                filter_ph_mark_rm(rm_ph_max, i_max, rm_ph_min, i_min);
            if(extrDiff_highSide < flt.ph[0])
                filter_ph_mark_rm(rm_ph_max, i_max, rm_ph_min, i_min);

            // extrDiff > ph max
            if(flt.ph_num == 2){
                if(extrDiff_lowSide > flt.ph[1])
                    filter_ph_mark_rm(rm_ph_max, i_max, rm_ph_min, i_min);
                if(extrDiff_highSide > flt.ph[1])
                    filter_ph_mark_rm(rm_ph_max, i_max, rm_ph_min, i_min);
            }
            ++i_max;
            ++i_min;
        }

        // if last extrema is max, check extrDiff_lowSide
        if(i_max == i_max_len){
            extrDiff_lowSide = data[list_data_get(rec_max, i_max)] - data[list_data_get(rec_min, i_min)] ;

            if(extrDiff_lowSide < flt.ph[0])
                filter_ph_mark_rm(rm_ph_max, i_max, rm_ph_min, i_min);
            if(flt.ph_num == 2)
                if(extrDiff_lowSide > flt.ph[1])
                    filter_ph_mark_rm(rm_ph_max, i_max, rm_ph_min, i_min);
        }

        
        // end ph filter, merge rm mark  
        if(rm_max != NULL){
            List *rm_max_new = merge_lists_uniq(rm_max, rm_ph_max);
            list_free(rm_max) ;
            rm_max = rm_max_new ;
            list_free(rm_ph_max) ;
        } else
            rm_max = rm_ph_max ;

        if(rm_min != NULL){
            List *rm_min_new = merge_lists_uniq(rm_min, rm_ph_min);
            list_free(rm_min) ;
            rm_min = rm_min_new ;
            list_free(rm_ph_min) ;
        } else
            rm_min = rm_ph_min ;

    } // end filter for ph


    // filter for flt.th (Threshold)

    if(flt.th_num > 0){
        List *rm_th_max = new_slist() ;
        List *rm_th_min = new_slist() ;
        unsigned long orig_max_i_len = list_data_total(rec_max) ;
        unsigned long orig_min_i_len = list_data_total(rec_min) ;
        double check_data ;
        switch(flt.th_num){
            case 1 :
                // rm all_low
                for(unsigned long i = 0; i < orig_min_i_len ; i++){
                    check_data = data[ list_data_get(rec_min, i) ] ;
                    if(check_data < flt.th[0])
                        list_data_append(rm_th_min, i);
                }
                for(unsigned long i = 0; i < orig_max_i_len ; i++){
                    check_data = data[ list_data_get(rec_max, i) ] ;
                    if(check_data < flt.th[0])
                        list_data_append(rm_th_max, i);
                }
                break ;

            case 2 :
                // [all_low all_up]
                for(unsigned long i = 0; i < orig_min_i_len ; i++){
                    check_data = data[ list_data_get(rec_min, i) ] ;
                    if( check_data < flt.th[0] || check_data > flt.th[1] )
                        list_data_append(rm_th_min, i);
                }
                for(unsigned long i = 0; i < orig_max_i_len ; i++){
                    check_data = data[ list_data_get(rec_max, i) ] ;
                    if( check_data < flt.th[0] || check_data > flt.th[1] )
                        list_data_append(rm_th_max, i);
                }
                break ;
            case 4 :
                // [[min_low,min_up],[min_low,min_up]]
                for(unsigned long i = 0; i < orig_min_i_len ; i++){
                    check_data = data[ list_data_get(rec_min, i) ] ;
                    if( check_data < flt.th[0] || check_data > flt.th[1] )
                        list_data_append(rm_th_min, i);
                }
                for(unsigned long i = 0; i < orig_max_i_len ; i++){
                    check_data = data[ list_data_get(rec_max, i) ] ;
                    if( check_data < flt.th[2] || check_data > flt.th[3] )
                        list_data_append(rm_th_max, i);
                }
                break ;
        }
        
        // end th filter, merge rm mark
        if(rm_max != NULL){
            List *rm_max_new = merge_lists_uniq(rm_max, rm_th_max);
            list_free(rm_max) ;
            rm_max = rm_max_new ;
            list_free(rm_th_max) ;
        } else
            rm_max = rm_th_max ;

        if(rm_min != NULL){
            List *rm_min_new = merge_lists_uniq(rm_min, rm_th_min);
            list_free(rm_min) ;
            rm_min = rm_min_new ;
            list_free(rm_th_min) ;
        } else
            rm_min = rm_th_min ;
    } // end filter for th

    
    // ------------------------------------------
    // finish filters, export list to return type.
    // ------------------------------------------
        
    if(flt.ph_num > 0 || flt.th_num > 0){


        // --------------------------
        // Export marked extrema (rm_max/rm_min)
        // --------------------------
        
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

    // Export filted extrema
    
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

    // clear lists

    list_free(rec_max) ;
    list_free(rec_min) ;
    
    if(rm_max)
        list_free(rm_max) ;
    if(rm_min)
        list_free(rm_min) ;
    
    return extrema_info ;
}

int main(){
    // Get your data[] ;
    //     double data[] = { 2,4,5,6,1,25,6};
    double data[] = {1, 1, 1.1, 1, 0.9, 1, 1, 1.1, 1, 0.9, 1, 1.1, 1, 1, 0.9, 1, 1, 1.1, 1, 1, 1, 1, 1.1, 0.9, 1, 1.1, 1, 1, 0.9, 1, 1.1, 1, 1, 1.1, 1, 0.8, 0.9, 1, 1.2, 0.9, 1, 1, 1.1, 1.2, 1, 1.5, 1, 3, 2, 5, 3, 2, 1, 1, 1, 0.9, 1, 1, 3, 2.6, 4, 3, 3.2, 2, 1, 1, 0.8, 4, 4, 2, 2.5, 1, 1, 1} ;

    // set filters. 
    struct Filters flt = {
        .pd = 5,
        .ph_num = 2,
        .ph = {0, 3.3} ,  // member <= 2, bug {0, 3.3}
        .th_num = 0 ,
        .th = {1}// {0.9,0.9,1,3}         // member <= 4 , != 3
    } ;
        
    // Use peak_detect() get extremas.
    Extrema_info extrema_info = peak_detect(data, sizeof(data)/sizeof(data[0]), flt);
    
//     return 0;
    // Print result.
    for(int i = 0; i < extrema_info.max_i_len; i++)
        printf("max[%d]\t-> data[%lu] = %g \n",i ,extrema_info.max_i[i], data[extrema_info.max_i[i]]);
    for(int i = 0; i < extrema_info.min_i_len; i++)
        printf("min[%d]\t-> data[%lu] = %g\n",i ,extrema_info.min_i[i], data[extrema_info.min_i[i]]);
    for(int i = 0; i < extrema_info.rm_max_len; i++)
        printf("rm_max[%d]\t -> data[%lu] = %g\n",i ,extrema_info.rm_max[i], data[extrema_info.rm_max[i]]);
    for(int i = 0; i < extrema_info.rm_min_len; i++)
        printf("rm_min[%d]\t-> data[%lu] = %g\n",i ,extrema_info.rm_min[i], data[extrema_info.rm_min[i]]);
    return 0;
}



