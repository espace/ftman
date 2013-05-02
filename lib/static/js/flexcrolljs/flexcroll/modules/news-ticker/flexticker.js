//Removable comments-start-
//Start the news ticker in any way you like, here we use the fake event, window.onfleXcrollRun, 
//onfleXcrollRun is a function that is run after fleXroll initializes
//Removable comments-end-

window.onfleXcrollRun=function(){
fleXnewsTicker('mycustomscroll',2,35,0.3,false,false,false);
fleXnewsTicker('mycustomscroll2',3,35,1,1800,1800,false);
}

//Removable comments-start-
//stepPerFrame: how much to scroll each frame in pixels
//frameLengh: miliseconds interval value for each frame
//            the smaller, the more frequent updates, but more CPU usage.
//            Making this smaller than 15 miliseconds is never beneficial
//            slow computers may choke if you use this too small.
//acceleratioN: how many steps to slow down each time hovered in and hovered out
//             make this bigger than the steps if you want instant stops
//startWait: how long to wait at the beginning, in miliseconds, at the beginning
//endWait: how long to wait at the beginning, in miliseconds, at the end
//waitOnce: only wait at the start of the scroll for once when first scroll starts
//             accepted values: true||false
//Removable comments-end-

function fleXnewsTicker(targetDivId,stepsPerFrame,frameLength,acceleratioN,startWait,endWait,waitOnce) {
//fleXcroll V-scrolling News Ticker Module By Hesido
//Version 1.1

	if(typeof(fleXenv)=="undefined") return false;
	var fDiv=document.getElementById(targetDivId),sPos,actSteps=0,tData=[];
	if (fDiv==null) return false;
	if (!fDiv.fleXcroll) fleXenv.fleXcrollMain(fDiv);

	fleXenv.addTrggr(fDiv,'mouseover', function(){tData.tickerHover=true;});
	fleXenv.addTrggr(fDiv,'mouseout', function(){tData.tickerHover=false;startScroll();});

	initScroll();

	function initScroll(reStart){
	if(reStart&&!tData.tickerHover) sPos=fDiv.fleXcroll.setScrollPos(false,0);
	if(startWait&&((reStart&&!waitOnce)||!reStart))  {
		if(tData.restartTimeout) window.clearTimeout(tData.restartTimeout);
		tData.restartTimeout=window.setTimeout(function(){startScroll(reStart)},startWait)
		}
	else startScroll();
	};
	
	function startScroll(){
	if(tData.tickInterval) return;
	tData.tickInterval=window.setInterval(function(){
		if(tData.tickerHover&&actSteps>0) actSteps=Math.max(0,actSteps-acceleratioN);
		if(actSteps<stepsPerFrame&&!tData.tickerHover) actSteps=Math.min(stepsPerFrame,actSteps+acceleratioN);
		sPos=fDiv.fleXcroll.scrollContent(false,actSteps+'px');
			if(sPos[1][0]==sPos[1][1]) {if(endWait) tPause(endWait); else tPause(frameLength);}
			else if(tData.startTimeout) window.clearTimeout(tData.startTimeout);
		if(actSteps===0) {window.clearTimeout(tData.tickInterval);tData.tickInterval=false;};
	}
	,frameLength);
	};
	
	var tPause=function(waitMsec){
			if(tData.tickInterval) window.clearTimeout(tData.tickInterval);tData.tickInterval=false;
			if(tData.startTimeout) window.clearTimeout(tData.startTimeout);
			tData.startTimeout=window.setTimeout(function(){initScroll(true)},waitMsec);
		};
};
