/*
Follow ups are defined as blood draws no more than on therapy after a
line treatment
This will take a obj of blood draws. Where each blooddraw object will contain
several keys.
Keys:
drawDate: int (ms)
LineInt: Int e.g. 0, 1, 2, 3 (0 refers to Baseline etc)
Followup: boolean e.g. true
PseudoFollowup: boolean e.g. false
surge: String e.g. 'exoDNA'

therapyObject = {
    Line:
    start: ms
    end: ms
};
The initial keys are the same as the start.
And compare to an array of therapy dates.
*/

blooddraws = {};
// blood draws populated through creation of graph
therapies = {};
// populated before this

// determines line/followup/pseudofollowups
var bdkeys = blooddraws.keys
var thkeys = therapies.keys

// while loop that keeps track of both
function followUps(bdkeys, blooddraws, thkeys, therapies){
    var i = 0,
        j = 0,
        k = 1,
        thmoves = 0;
    if(blooddraws[bdkeys[0]].drawDate <= therapies[thkeys[0]].start){
        blooddraws[bdkeys[0]].line = 'Baseline';
    };

    while( i < bdkeys.length - 1 && j < thkeys.length && k < bdkeys.length){
        if(k <= i){k = i + 1};
        var bd = blooddraws[bdkeys[i]],
            bd2 = blooddraws[bdkeys[k]],
            th = therapies[thkeys[j]];
        // check where bd2 is in regards to current therapy
        // check to see if it's before the end of therapy
        if(bd.line){
            if(bd2.drawDate < th.end){
                // check to see if after the start
                if(bd2.drawDate > th.start && thmoves == 0){
                    bd2['pseudoFollowup'] = true;
                    k++;
                // if not after start, means this therapy happens after this bd
                } else if( bd2.drawDate <= th.start && thmoves == 1){
                    if(therapies[thkeys[j-1]].line != th.line){
                        bd2['followUp'] = true;
                        if(!bd2.line){
                            bd2.line = therapies[thkeys[j-1]].line;
                        };
                        i = k;
                        k++;
                        thmoves = 0;
                    } else{
                        bd2['pseudoFollowup'] = true;
                        k++;
                        thmoves = 0;
                    };
                };
                // see if it takes place after end
            } else if (bd2.drawDate > th.end){
                //
                if(j + 1 == thkeys.length && thmoves == 0){
                    bd2['followUp'] = true;
                    bd2.line = th.line;
                    j++;
                } else {
                    if(bd2.drawDate < therapies[thkeys[j+1]].start){
                        bd2.line = th.line;
                    };
                    if(thmoves == 0) {
                        j++;
                        thmoves++;
                    } else {
                        i = k;
                        k++;
                        thmoves = 0;
                    };
                };
            };
        } else {
            // check if actually has a line
            if(bd.drawDate > th.start){
                if(bd.drawDate < th.end){
                    i++;
                } else {
                    j++;
                    thmoves++;
                };
            } else if (bd.drawDate <= th.start){
                    if(thmoves >= 1){
                        bd.line = therapies[thkeys[j-1]].line;
                    } else {
                        i++;
                    };
            };
        };
    };

};

/*
Lag time is defined as the time between a kras surge and progression.
To find lag time, we use the same blood draws object but compare it to a
progression object
Each key is a progression. The progression keys:
Date: int (ms)
Lagtime: int

Function will take progression. Looks for first blooddraw to the left
with a surge key.
if exists, find the time difference between the two.

Uses
*/

var progression = {};


// grabs the first progression and looks for the earliest blood draw with
// a kras surge.
// returns the time in MS between that draw and the progression.
// If there is no progression then the date of death is used instead.
function lagTime(blooddraws, progression){
    var bdkeys = blooddraws.keys,
        pgkeys = progression.keys,
        i = 0,
        j = 0;

    while( i < bdkeys.length && j < pgkeys.length ){
        var progdate = progression[pgkeys[j]],
            bddate = blooddraws[bdkeys[i]];
        if(bddate.drawDate > progdate.Date){
            j++;
        } else if(bddate.surge){
            return progdate.Date - bddate.surge;
        } else {
            i++;
        };
    } else {
        return 0;
    };
};
