/* 
Takes in therapies and recist objects.
Returns an array of arrays, with index 0 being the start date and 1 being the end date.

---> scrap this
*/
function createDateRanges(therapies, recist){
    var thkeys = Object.keys(therapies),
        rskeys = Object.keys(recist),
        s = 1,
        r = 0,
        bool = false,
        firstCT = recist[rskeys[0]],
        ranges = [];
// first take in qualifiers (e.g. only 1 CT)
    if (rskeys.length < 2) {return 'Not enough CT''s'};
// Otherwise loop through each therapy. And find the corresponding ranges based on that
// *Note, there are patients who have separate therapies with the same line
    for(var i = 0; i < thkeys.length; i++){
        var th = therapies[thkeys[i]];
        //while the indexes are still under the length.
        while(s < rskeys.length){
            var rsStart = recist[rskeys[r]];
            var rsEnd = recist[rskeys[s]];
            // if the first ct is before this therapy while the next ct is after the start
            // Then we can start comparing to find the last staging event
            if(rsStart['imageDate'] <= th['start'] && rsEnd['imageDate'] >= th['start']){
                // if the end CT is before this therapy end move to next CT.
                // note: The final restaging sometimes is within the therapy
                if(rsEnd['imageDate'] <= th['end']){
                    if(s + 1 < rskeys.length){
                        s += 1;
                    } else {
                        console.log('Image is last one');
                        break};
                // if end CT is after the the therapy
                } else if(rsEnd['imageDate'] >= th['end']){
                    //check if it's also after the start of next therapy
                    if(thkeys[i+1]){
                        //first check if next therapy is same line
                        if(therapies[thkeys[i+]].line = th.line){
                        	i += 1;
                            s += 1;
                        //then check if it's after the start of the next therapy, if it is, then the previous CT was the last restaging. And break out of loop
                        } else if(rsEnd['imageDate'] > therapies[thkeys[i+1]]['start']){
                            s -= 1;
                            break;
                        } else {break;};
                    } else { break;};
                } else {};
            // if first ct start date is after the start of therapy 
            } else if(rsStart['imageDate'] > th['start']) {
                bool = true;
            } else {
                r += 1;
                s += 1;
            };
        };
        if(bool = false){
            var startDate = recist[rskeys[r]]['imageDate'];        
        } else {
            var startDate = th['start'];
        };
        var endDate = recist[rskeys[s]]['imageDate'];
        ranges.push([startDate, endDate, 'R' + i + 'S' + s-r]);
        r = s; 
        s += 1;
    };
};


function createDateRanges(therapies, recist){
    var thkeys = Object.keys(therapies),
        rskeys = Object.keys(recist),
        r = 0,
        regimen = 0,
        pline = '',
        bool = false,
        firstCT = recist[rskeys[0]],
        ranges = [];
    // first take in qualifiers (e.g. only 1 CT)
    if (rskeys.length < 2) {
        console.log('not of CT scans');
      return
    };
    /*
     The start of each RX is the therapy start date, the end date(s) are the CT's
     that show up in within the therapy.
     Exceptions will show up with the final CT being near the beginning of the following surgery
    */
    for(var i = 0; i < thkeys.length; i++){
        var th = therapies[thkeys[i]],
            s = 0;

        if(pline != th.line || pline == ''){
            pline = th.line;
            regimen += 1;
        };
        //while the indexes are still under the length.
        while(bool == false && r < rskeys.length){
            var rsImage = recist[rskeys[r]];
            //is the image before therapy?
            if(rsImage['imageDate'] < th['start']){
                r += 1;
            } else {
                //check if therapy is before the end of therapy
                if(rsImage['imageDate'] <= th['end']){
                    // if it is, push to ranges
                    s += 1;
                    r += 1;
                    ranges.push({
                        R: regimen,
                        S: s,
                        start: th['start'],
                        end: rsImage['imageDate']
                    });
                //if therapy is after end, we have to run two tests
                } else {
                    //check to see if there is a therapy after
                    if(thkeys[i+1]){
                        // check to see if after the end
                        if(therapies[thkeys[i+1]]['end'] <= rsImage['imageDate']){
                            // move to next therapy
                            bool = true;
                        // see if before the start of the next therapy, if so push and then end
                        } else if(therapies[thkeys[i+1]]['start'] >= rsImage['imageDate']) {
                            s += 1;
                            r += 1;
                            ranges.push({
                                R: regimen,
                                S: s,
                                start: th['start'],
                                end: rsImage['imageDate']
                            });
                            bool = true;
                        // if none of above, see if it's within 2 weeks of start of therapy and if there was already restaging
                        // don't increase r here, since it will be referenced for this next therapy
                        } else if(Math.abs(therapies[thkeys[i+1]]['start'] - rsImage['imageDate']) < 604800000 && s == 0){
                            s += 1;
                            ranges.push({
                                R: regimen,
                                S: s,
                                start: th['start'],
                                end: rsImage['imageDate']
                            });
                            bool = true;
                        } else { bool = true};
                    } else {
                        ranges.push({
                            R: regimen,
                            S: s
                            start: th['start'],
                            end: rsImage['imageDate']
                        });
                        bool = true;
                    };
                };
            };    
        };
        bool = false;
    };
    return ranges;
};

/*
    After finding the ranges, iterate through blooddraws and label them with the regimen and stagings
    note to self. can I avoid a n^2 solution?
*/
function assignRS(ranges, blooddraws){
    var ranges = ranges,
        blooddraws = blooddraws,
        looper = 0,
        bdkeys = Object.keys(blooddraws);

    // go through each blooddraw
    for(var i = 0; i < bdkeys.length; i++){
        var bddd = blooddraws[bdkeys[i]]['drawDate'];
        //compare to ranges
        for(var j = 0; j < ranges.length; j++){
            var range = ranges[j];
            if(bddd >= range.start && bddd <= range.end){
                if(blooddraws[bdkeys[i]]['R']){
                    bloodraws[bdkeys[i]]['R'].push(range.R);
                    blooddraw[bdkeys[i]]['S'].push(range.S);
                } else {
                    blooddraws[bdkeys[i]]['R'] = [range.R];
                    blooddraws[bdkeys[i]]['S'] = [range.S];          
                };
            }
        }; 
    };
    return blooddraws;
};