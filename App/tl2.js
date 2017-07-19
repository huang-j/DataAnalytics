/* 
Takes in therapies and recist objects.
Returns an array of arrays, with index 0 being the start date and 1 being the end date.
*/
function createDateRanges(therapies, recist){
    var thkeys = Object.keys(therapies),
        rskeys = Object.keys(recist),
        s = 1,
        r = 0,
        firstCT = recist[rskeys[0]],
        ranges = [];
// first take in qualifiers (e.g. only 1 CT)
    if (rskeys.length < 2) {return 'Not enough CT''s'};
// Otherwise loop through each therapy. And find the corresponding ranges based on that
// *Note, there are patients who have separate therapies with the same line
    for(var i = 0; i < thkeys.length; i++){
        var th = therapies[thkeys[i]];
        while(r + s < rskeys.length){
            var rsStart = recist[rskeys[r]];
            var rsEnd = recist[rskeys[s]];
            // if the first ct is before this therapy while the next ct is after the start
            // Then we can start comparing to find the last staging event
            if(rsStart['imageDate'] <= th['start'] && rsEnd['imageDate'] >= th['start']){
                // if the end CT is before this therapy end move to next CT.
                // note: The final restaging sometimes is within the therapy
                if(rsEnd['imageDate'] <= th['end']){
                    s += 1;
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
            } 
        };
    };
};
