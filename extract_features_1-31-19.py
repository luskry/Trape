def extract_features(seq_window_merged_refined_utrs_file, tmp_dir, bedgraph_files):
    
    window_size = 100
    signal_window_size = 36
    min_upstream_signal_size = 7
    UTR_events_dict = {}
    All_Samples_Total_depth = []
    All_samples_extracted_3UTR_coverage_dict = {}
    All_samples_extracted_3UTR_coverage_dict_minus = {}
    features_dict = {}

    with open(tmp_dir+seq_window_merged_refined_utrs_file, 'r') as f:
            for line in f:
                fields = line.strip('\n').split('\t')
                name = fields[3]
                start = int(fields[1])
                end = int(fields[2])
                bases = fields[-1]
                
                for idx, i in enumerate(range(start, end - window_size * 2, window_size)):
                    region_start = i
                    region_end = i + window_size * 3
                    rel_start = idx * window_size
                    rel_end = (idx + 3) * window_size
                    utr_pos = '%s-%s' % (i + window_size, i + window_size * 2)
                    curr_bases = bases[rel_start + window_size - signal_window_size:rel_end - window_size - min_upstream_signal_size]
                    UTR_events_dict['%s|%s-%s' % (name, i + window_size, i + window_size * 2)] = [fields[0], region_start, region_end, fields[5], utr_pos, curr_bases]      
    
    for curr_3UTR_event_id in UTR_events_dict:
        features_dict[curr_3UTR_event_id] = []
        curr_3UTR_structure = UTR_events_dict[curr_3UTR_event_id]
        curr_chr = curr_3UTR_structure[0]
        bases = UTR_events_dict[curr_3UTR_event_id][-1]
        features_dict[curr_3UTR_event_id].append(signal_variant_indicator(bases, ['AATAAA', 'ATTAAA']))
        features_dict[curr_3UTR_event_id].append(signal_variant_indicator(bases, ['AAGAAA', 'AAAAAG', 'AATACA', 'TATAAA', 'ACTAAA', 'AGTAAA', 'GATAAA', 'AATATA', 'CATAAA', 'AATAGA']))                  
    
    for curr_bedgraph in bedgraph_files:
        cur_sample_total_depth = 0
        num_line = 0
        curr_sample_All_chroms_coverage_dict = {}
        curr_sample_All_chroms_coverage_dict_minus = {}
        
        with open(tmp_dir+curr_bedgraph, 'r') as f:
            for line in f:
                if '#' not in line:
                    fields = line.strip('\n').split('\t')
                    chrom_name = fields[0]
                    if not chrom_name.startswith('chr'):
                          chrom_name = 'chr' + chrom_name
                    region_start = int(float(fields[1]))
                    region_end = int(float(fields[2]))
                    cur_sample_total_depth += int(float(fields[-2])) * (region_end - region_start) + int(float(fields[-1])) * (region_end - region_start)
                    
                    if chrom_name not in curr_sample_All_chroms_coverage_dict:
                        curr_sample_All_chroms_coverage_dict[chrom_name] = [[0],[0]]
                    if region_start > curr_sample_All_chroms_coverage_dict[chrom_name][0][-1]:
                        curr_sample_All_chroms_coverage_dict[chrom_name][0].append(region_start)
                        curr_sample_All_chroms_coverage_dict[chrom_name][1].append(0)
                    curr_sample_All_chroms_coverage_dict[chrom_name][0].append(region_end)
                    curr_sample_All_chroms_coverage_dict[chrom_name][1].append(int(float(fields[-2])))
            
                    if chrom_name not in curr_sample_All_chroms_coverage_dict_minus:
                        curr_sample_All_chroms_coverage_dict_minus[chrom_name] = [[0],[0]]
                    if region_start > curr_sample_All_chroms_coverage_dict_minus[chrom_name][0][-1]:
                        curr_sample_All_chroms_coverage_dict_minus[chrom_name][0].append(region_start)
                        curr_sample_All_chroms_coverage_dict_minus[chrom_name][1].append(0)
                    curr_sample_All_chroms_coverage_dict_minus[chrom_name][0].append(region_end)
                    curr_sample_All_chroms_coverage_dict_minus[chrom_name][1].append(int(float(fields[-1])))
                num_line += 1
        All_Samples_Total_depth.append(cur_sample_total_depth)
        curr_sample_All_chroms_coverage_dict[chrom_name][1].append(0)
        curr_sample_All_chroms_coverage_dict_minus[chrom_name][1].append(0)    
    
        for curr_3UTR_event_id in UTR_events_dict:
            curr_3UTR_structure = UTR_events_dict[curr_3UTR_event_id]
            curr_chr = curr_3UTR_structure[0]
            curr_3UTR_all_samples_bp_coverage = []
            exp_list = [] 
            
            if UTR_events_dict[curr_3UTR_event_id][-3] == '+':
                if curr_chr in curr_sample_All_chroms_coverage_dict:
                    curr_chr_coverage = curr_sample_All_chroms_coverage_dict[curr_chr]
                    region_start = int(float(curr_3UTR_structure[1]))
                    region_end = int(float(curr_3UTR_structure[2]))
                    left_region_index = bisect(curr_chr_coverage[0],region_start)
                    right_region_index = bisect(curr_chr_coverage[0],region_end)
                    extracted_coverage = curr_chr_coverage[1][left_region_index:right_region_index+1]
                    extracted_3UTR_region = curr_chr_coverage[0][left_region_index:right_region_index]
                    extracted_3UTR_region.insert(0,region_start)
                    extracted_3UTR_region.append(region_end)
                    
                    if curr_3UTR_event_id not in All_samples_extracted_3UTR_coverage_dict:
                        All_samples_extracted_3UTR_coverage_dict[curr_3UTR_event_id] = []
                    All_samples_extracted_3UTR_coverage_dict[curr_3UTR_event_id].append([extracted_coverage,extracted_3UTR_region])
           
            elif UTR_events_dict[curr_3UTR_event_id][-3] == '-':
                if curr_chr in curr_sample_All_chroms_coverage_dict_minus:
                    curr_chr_coverage = curr_sample_All_chroms_coverage_dict_minus[curr_chr]
                    region_start = int(float(curr_3UTR_structure[1]))
                    region_end = int(float(curr_3UTR_structure[2]))
                    left_region_index = bisect(curr_chr_coverage[0],region_start)
                    right_region_index = bisect(curr_chr_coverage[0],region_end)
                    extracted_coverage = curr_chr_coverage[1][left_region_index:right_region_index+1]
                    extracted_3UTR_region = curr_chr_coverage[0][left_region_index:right_region_index]
                    extracted_3UTR_region.insert(0,region_start)
                    extracted_3UTR_region.append(region_end)
                    
                    if curr_3UTR_event_id not in All_samples_extracted_3UTR_coverage_dict_minus:
                        All_samples_extracted_3UTR_coverage_dict_minus[curr_3UTR_event_id] = []
                    All_samples_extracted_3UTR_coverage_dict_minus[curr_3UTR_event_id].append([extracted_coverage,extracted_3UTR_region])
    
            if UTR_events_dict[curr_3UTR_event_id][-3] == '-' and curr_3UTR_event_id in All_samples_extracted_3UTR_coverage_dict_minus:
                curr_3UTR_coverage_wig = All_samples_extracted_3UTR_coverage_dict_minus[curr_3UTR_event_id]
                for curr_sample_curr_3UTR_coverage_wig in curr_3UTR_coverage_wig: 
                    bp_coverage = np.zeros(curr_sample_curr_3UTR_coverage_wig[1][-1] - curr_sample_curr_3UTR_coverage_wig[1][0])
                    relative_start = curr_sample_curr_3UTR_coverage_wig[1][0]
                    for i in range(len(curr_sample_curr_3UTR_coverage_wig[0])):
                        curr_region_start = curr_sample_curr_3UTR_coverage_wig[1][i] - relative_start
                        curr_region_end = curr_sample_curr_3UTR_coverage_wig[1][i+1] - relative_start
                        bp_coverage[curr_region_start:curr_region_end] = curr_sample_curr_3UTR_coverage_wig[0][i]
                    bp_coverage = bp_coverage[::-1]
                    curr_3UTR_all_samples_bp_coverage.append(bp_coverage)
            elif UTR_events_dict[curr_3UTR_event_id][-3] == '+' and curr_3UTR_event_id in All_samples_extracted_3UTR_coverage_dict:
                curr_3UTR_coverage_wig = All_samples_extracted_3UTR_coverage_dict[curr_3UTR_event_id]
                for curr_sample_curr_3UTR_coverage_wig in curr_3UTR_coverage_wig: 
                    bp_coverage = np.zeros(curr_sample_curr_3UTR_coverage_wig[1][-1] - curr_sample_curr_3UTR_coverage_wig[1][0])
                    relative_start = curr_sample_curr_3UTR_coverage_wig[1][0]
                    for i in range(len(curr_sample_curr_3UTR_coverage_wig[0])):
                        curr_region_start = curr_sample_curr_3UTR_coverage_wig[1][i] - relative_start
                        curr_region_end = curr_sample_curr_3UTR_coverage_wig[1][i+1] - relative_start
                        bp_coverage[curr_region_start:curr_region_end] = curr_sample_curr_3UTR_coverage_wig[0][i]
                    curr_3UTR_all_samples_bp_coverage.append(bp_coverage)
              
             
            for i in range(len(curr_3UTR_all_samples_bp_coverage)):
                cov_array = curr_3UTR_all_samples_bp_coverage[i]
                reg_one = (np.mean(cov_array[0:window_size])*1000000)/(np.array(All_Samples_Total_depth)[i]/1000000)
                reg_two = (np.mean(cov_array[window_size:2*window_size])*1000000)/(np.array(All_Samples_Total_depth)[i]/1000000)
                reg_three = (np.mean(cov_array[2*window_size:3*window_size])*1000000)/(np.array(All_Samples_Total_depth)[i]/1000000)
                two_one_diff = abs(reg_two-reg_one)
                three_two_diff = abs(reg_two-reg_three)
                overall_diff = two_one_diff+three_two_diff
                exp_list.append(overall_diff)          
            features_dict[curr_3UTR_event_id].append(sum(exp_list))       
    
    return features_dict
