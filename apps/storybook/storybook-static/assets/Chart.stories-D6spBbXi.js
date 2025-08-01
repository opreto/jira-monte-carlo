import{j as d}from"./jsx-runtime-D_zvdyIk.js";import{C as D,c as e,a}from"./constants-CSgdsXDf.js";import"./index-0yr9KlQE.js";import"./utils-CytzSlOG.js";const Y={title:"Components/Chart",component:D,tags:["autodocs"],parameters:{layout:"padded"}},t={args:{title:"Sprint Velocity Trend",data:[{x:["Sprint 37","Sprint 38","Sprint 39","Sprint 40","Sprint 41","Sprint 42"],y:[46,40,44,35,48,42],type:"scatter",mode:"lines+markers",name:"Completed",line:{color:a.primary[0],width:3},marker:{size:8}},{x:["Sprint 37","Sprint 38","Sprint 39","Sprint 40","Sprint 41","Sprint 42"],y:[48,42,45,40,50,45],type:"scatter",mode:"lines+markers",name:"Committed",line:{color:a.categorical[1],width:2,dash:"dash"},marker:{size:6}}],layout:{...e.timeSeries,yaxis:{...e.timeSeries.yaxis,title:"Story Points"}}}},n={args:{title:"Sprint 42 Burndown",data:[{x:["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7","Day 8","Day 9","Day 10"],y:[45,45,42,38,35,30,28,22,15,8],type:"scatter",mode:"lines+markers",name:"Actual",line:{color:a.primary[0],width:3},fill:"tozeroy",fillcolor:"rgba(3, 86, 76, 0.1)"},{x:["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7","Day 8","Day 9","Day 10"],y:[45,40.5,36,31.5,27,22.5,18,13.5,9,4.5],type:"scatter",mode:"lines",name:"Ideal",line:{color:a.categorical[1],width:2,dash:"dash"}}],layout:{yaxis:{title:"Remaining Story Points",rangemode:"tozero"},xaxis:{title:"Sprint Days"}}}},r={args:{title:"Story Cycle Time Distribution",data:[{x:[1.2,2.3,1.8,3.4,2.1,4.5,2.8,1.5,3.2,2.7,5.1,2.4,3.8,1.9,2.6,4.2,3.1,2.2,1.7,3.5],type:"histogram",name:"Cycle Time (days)",marker:{color:a.primary[0]},opacity:.75,nbinsx:10}],layout:{...e.bar,xaxis:{title:"Cycle Time (days)"},yaxis:{title:"Number of Stories"},bargap:.05}}},i={args:{title:"Team Capacity Utilization",data:[{x:["Sarah Chen","Mike Johnson","Emily Davis","David Kim","Lisa Wang"],y:[95,88,92,78,90],type:"bar",name:"Current Sprint",marker:{color:a.primary[0]}},{x:["Sarah Chen","Mike Johnson","Emily Davis","David Kim","Lisa Wang"],y:[85,90,88,82,87],type:"bar",name:"3-Sprint Average",marker:{color:a.primary[2]}}],layout:{...e.bar,yaxis:{...e.bar.yaxis,title:"Capacity %",range:[0,100]},barmode:"group"}}},o={args:{title:"Defects by Priority",data:[{values:[2,8,15,32],labels:["Critical","High","Medium","Low"],type:"pie",hole:.4,marker:{colors:["#dc2626","#f97316","#eab308","#3b82f6"]},textinfo:"label+percent",textposition:"outside"}],layout:{...e.pie}}},s={args:{title:"Project Completion Probability",data:[{x:Array.from({length:100},(R,p)=>new Date(2025,2,1+p)),y:Array.from({length:100},(R,p)=>1/(1+Math.exp(-(p-50)/10))+(Math.random()-.5)*.1),type:"scatter",mode:"lines",name:"Completion Probability",line:{color:a.primary[0],width:3},fill:"tozeroy",fillcolor:"rgba(3, 86, 76, 0.2)"},{x:[new Date(2025,3,15),new Date(2025,3,15)],y:[0,1],type:"scatter",mode:"lines",name:"50% Confidence",line:{color:a.categorical[2],width:2,dash:"dash"}},{x:[new Date(2025,4,12),new Date(2025,4,12)],y:[0,1],type:"scatter",mode:"lines",name:"85% Confidence",line:{color:a.categorical[5],width:2,dash:"dot"}}],layout:{...e.timeSeries,yaxis:{...e.timeSeries.yaxis,title:"Completion Probability",tickformat:".0%",range:[0,1.05]},xaxis:{...e.timeSeries.xaxis,title:"Date"}}}},l={args:{title:"Story Points vs Cycle Time",data:[{x:[1,2,3,5,8,13,1,2,3,5,8,13,1,2,3,5,8],y:[.8,1.5,2.2,3.5,5.8,9.2,1.2,1.8,2.5,4.1,6.5,10.5,.9,1.6,2.8,3.8,7.2],mode:"markers",type:"scatter",name:"Stories",marker:{color:a.primary[0],size:10,opacity:.7}},{x:[1,13],y:[1,9],mode:"lines",type:"scatter",name:"Trend",line:{color:a.categorical[1],width:2,dash:"dash"}}],layout:{...e.scatter,xaxis:{...e.scatter.xaxis,title:"Story Points"},yaxis:{...e.scatter.yaxis,title:"Cycle Time (days)"}}}},y={args:{title:"Cumulative Flow Diagram",data:[{x:["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7","Day 8","Day 9","Day 10"],y:[45,45,45,45,45,45,45,45,45,45],type:"scatter",mode:"lines",name:"Total",stackgroup:"one",fillcolor:a.sequential.blue[2],line:{width:0}},{x:["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7","Day 8","Day 9","Day 10"],y:[0,0,3,7,10,15,17,23,30,37],type:"scatter",mode:"lines",name:"Done",stackgroup:"one",fillcolor:a.sequential.green[4],line:{width:0}},{x:["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7","Day 8","Day 9","Day 10"],y:[0,5,8,10,12,10,8,5,3,0],type:"scatter",mode:"lines",name:"In Progress",stackgroup:"one",fillcolor:a.sequential.blue[4],line:{width:0}},{x:["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7","Day 8","Day 9","Day 10"],y:[45,40,34,28,23,20,20,17,12,8],type:"scatter",mode:"lines",name:"To Do",stackgroup:"one",fillcolor:a.sequential.blue[2],line:{width:0}}],layout:{yaxis:{title:"Story Points"},xaxis:{title:"Sprint Days"}}}},c={args:{title:"Team Productivity Heatmap",data:[{z:[[8,12,15,10,5],[10,14,16,12,8],[12,16,18,14,10],[9,13,15,11,7],[6,10,12,8,4]],x:["Monday","Tuesday","Wednesday","Thursday","Friday"],y:["Week 1","Week 2","Week 3","Week 4","Week 5"],type:"heatmap",colorscale:[[0,a.sequential.green[0]],[.5,a.sequential.green[4]],[1,a.sequential.green[8]]],showscale:!0,colorbar:{title:"Story Points"}}],layout:{xaxis:{title:"Day of Week"},yaxis:{title:"Sprint Week"}}}},m={render:()=>d.jsxs("div",{className:"grid grid-cols-1 gap-4 md:grid-cols-2",children:[d.jsx(D,{title:"Sprint Velocity",data:[{x:["Sprint 40","Sprint 41","Sprint 42"],y:[35,48,42],type:"bar",marker:{color:a.primary[0]}}],layout:{...e.bar,height:300}}),d.jsx(D,{title:"Bug Distribution",data:[{values:[15,42,89,156],labels:["Critical","High","Medium","Low"],type:"pie",marker:{colors:a.categorical.slice(0,4)}}],layout:{...e.pie,height:300}})]})};var u,h,g;t.parameters={...t.parameters,docs:{...(u=t.parameters)==null?void 0:u.docs,source:{originalSource:`{
  args: {
    title: 'Sprint Velocity Trend',
    data: [{
      x: ['Sprint 37', 'Sprint 38', 'Sprint 39', 'Sprint 40', 'Sprint 41', 'Sprint 42'],
      y: [46, 40, 44, 35, 48, 42],
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Completed',
      line: {
        color: chartColors.primary[0],
        width: 3
      },
      marker: {
        size: 8
      }
    }, {
      x: ['Sprint 37', 'Sprint 38', 'Sprint 39', 'Sprint 40', 'Sprint 41', 'Sprint 42'],
      y: [48, 42, 45, 40, 50, 45],
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Committed',
      line: {
        color: chartColors.categorical[1],
        width: 2,
        dash: 'dash'
      },
      marker: {
        size: 6
      }
    }],
    layout: {
      ...chartLayouts.timeSeries,
      yaxis: {
        ...chartLayouts.timeSeries.yaxis,
        title: 'Story Points'
      }
    }
  }
}`,...(g=(h=t.parameters)==null?void 0:h.docs)==null?void 0:g.source}}};var x,S,C;n.parameters={...n.parameters,docs:{...(x=n.parameters)==null?void 0:x.docs,source:{originalSource:`{
  args: {
    title: 'Sprint 42 Burndown',
    data: [{
      x: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7', 'Day 8', 'Day 9', 'Day 10'],
      y: [45, 45, 42, 38, 35, 30, 28, 22, 15, 8],
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Actual',
      line: {
        color: chartColors.primary[0],
        width: 3
      },
      fill: 'tozeroy',
      fillcolor: 'rgba(3, 86, 76, 0.1)'
    }, {
      x: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7', 'Day 8', 'Day 9', 'Day 10'],
      y: [45, 40.5, 36, 31.5, 27, 22.5, 18, 13.5, 9, 4.5],
      type: 'scatter',
      mode: 'lines',
      name: 'Ideal',
      line: {
        color: chartColors.categorical[1],
        width: 2,
        dash: 'dash'
      }
    }],
    layout: {
      yaxis: {
        title: 'Remaining Story Points',
        rangemode: 'tozero'
      },
      xaxis: {
        title: 'Sprint Days'
      }
    }
  }
}`,...(C=(S=n.parameters)==null?void 0:S.docs)==null?void 0:C.source}}};var b,k,w;r.parameters={...r.parameters,docs:{...(b=r.parameters)==null?void 0:b.docs,source:{originalSource:`{
  args: {
    title: 'Story Cycle Time Distribution',
    data: [{
      x: [1.2, 2.3, 1.8, 3.4, 2.1, 4.5, 2.8, 1.5, 3.2, 2.7, 5.1, 2.4, 3.8, 1.9, 2.6, 4.2, 3.1, 2.2, 1.7, 3.5],
      type: 'histogram',
      name: 'Cycle Time (days)',
      marker: {
        color: chartColors.primary[0]
      },
      opacity: 0.75,
      nbinsx: 10
    }],
    layout: {
      ...chartLayouts.bar,
      xaxis: {
        title: 'Cycle Time (days)'
      },
      yaxis: {
        title: 'Number of Stories'
      },
      bargap: 0.05
    }
  }
}`,...(w=(k=r.parameters)==null?void 0:k.docs)==null?void 0:w.source}}};var f,T,P;i.parameters={...i.parameters,docs:{...(f=i.parameters)==null?void 0:f.docs,source:{originalSource:`{
  args: {
    title: 'Team Capacity Utilization',
    data: [{
      x: ['Sarah Chen', 'Mike Johnson', 'Emily Davis', 'David Kim', 'Lisa Wang'],
      y: [95, 88, 92, 78, 90],
      type: 'bar',
      name: 'Current Sprint',
      marker: {
        color: chartColors.primary[0]
      }
    }, {
      x: ['Sarah Chen', 'Mike Johnson', 'Emily Davis', 'David Kim', 'Lisa Wang'],
      y: [85, 90, 88, 82, 87],
      type: 'bar',
      name: '3-Sprint Average',
      marker: {
        color: chartColors.primary[2]
      }
    }],
    layout: {
      ...chartLayouts.bar,
      yaxis: {
        ...chartLayouts.bar.yaxis,
        title: 'Capacity %',
        range: [0, 100]
      },
      barmode: 'group'
    }
  }
}`,...(P=(T=i.parameters)==null?void 0:T.docs)==null?void 0:P.source}}};var v,L,W;o.parameters={...o.parameters,docs:{...(v=o.parameters)==null?void 0:v.docs,source:{originalSource:`{
  args: {
    title: 'Defects by Priority',
    data: [{
      values: [2, 8, 15, 32],
      labels: ['Critical', 'High', 'Medium', 'Low'],
      type: 'pie',
      hole: 0.4,
      marker: {
        colors: ['#dc2626', '#f97316', '#eab308', '#3b82f6']
      },
      textinfo: 'label+percent',
      textposition: 'outside'
    }],
    layout: {
      ...chartLayouts.pie
    }
  }
}`,...(W=(L=o.parameters)==null?void 0:L.docs)==null?void 0:W.source}}};var M,z,q;s.parameters={...s.parameters,docs:{...(M=s.parameters)==null?void 0:M.docs,source:{originalSource:`{
  args: {
    title: 'Project Completion Probability',
    data: [{
      x: Array.from({
        length: 100
      }, (_, i) => new Date(2025, 2, 1 + i)),
      y: Array.from({
        length: 100
      }, (_, i) => {
        const base = 1 / (1 + Math.exp(-(i - 50) / 10));
        return base + (Math.random() - 0.5) * 0.1;
      }),
      type: 'scatter',
      mode: 'lines',
      name: 'Completion Probability',
      line: {
        color: chartColors.primary[0],
        width: 3
      },
      fill: 'tozeroy',
      fillcolor: 'rgba(3, 86, 76, 0.2)'
    }, {
      x: [new Date(2025, 3, 15), new Date(2025, 3, 15)],
      y: [0, 1],
      type: 'scatter',
      mode: 'lines',
      name: '50% Confidence',
      line: {
        color: chartColors.categorical[2],
        width: 2,
        dash: 'dash'
      }
    }, {
      x: [new Date(2025, 4, 12), new Date(2025, 4, 12)],
      y: [0, 1],
      type: 'scatter',
      mode: 'lines',
      name: '85% Confidence',
      line: {
        color: chartColors.categorical[5],
        width: 2,
        dash: 'dot'
      }
    }],
    layout: {
      ...chartLayouts.timeSeries,
      yaxis: {
        ...chartLayouts.timeSeries.yaxis,
        title: 'Completion Probability',
        tickformat: '.0%',
        range: [0, 1.05]
      },
      xaxis: {
        ...chartLayouts.timeSeries.xaxis,
        title: 'Date'
      }
    }
  }
}`,...(q=(z=s.parameters)==null?void 0:z.docs)==null?void 0:q.source}}};var B,H,A;l.parameters={...l.parameters,docs:{...(B=l.parameters)==null?void 0:B.docs,source:{originalSource:`{
  args: {
    title: 'Story Points vs Cycle Time',
    data: [{
      x: [1, 2, 3, 5, 8, 13, 1, 2, 3, 5, 8, 13, 1, 2, 3, 5, 8],
      y: [0.8, 1.5, 2.2, 3.5, 5.8, 9.2, 1.2, 1.8, 2.5, 4.1, 6.5, 10.5, 0.9, 1.6, 2.8, 3.8, 7.2],
      mode: 'markers',
      type: 'scatter',
      name: 'Stories',
      marker: {
        color: chartColors.primary[0],
        size: 10,
        opacity: 0.7
      }
    }, {
      x: [1, 13],
      y: [1, 9],
      mode: 'lines',
      type: 'scatter',
      name: 'Trend',
      line: {
        color: chartColors.categorical[1],
        width: 2,
        dash: 'dash'
      }
    }],
    layout: {
      ...chartLayouts.scatter,
      xaxis: {
        ...chartLayouts.scatter.xaxis,
        title: 'Story Points'
      },
      yaxis: {
        ...chartLayouts.scatter.yaxis,
        title: 'Cycle Time (days)'
      }
    }
  }
}`,...(A=(H=l.parameters)==null?void 0:H.docs)==null?void 0:A.source}}};var j,E,F;y.parameters={...y.parameters,docs:{...(j=y.parameters)==null?void 0:j.docs,source:{originalSource:`{
  args: {
    title: 'Cumulative Flow Diagram',
    data: [{
      x: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7', 'Day 8', 'Day 9', 'Day 10'],
      y: [45, 45, 45, 45, 45, 45, 45, 45, 45, 45],
      type: 'scatter',
      mode: 'lines',
      name: 'Total',
      stackgroup: 'one',
      fillcolor: chartColors.sequential.blue[2],
      line: {
        width: 0
      }
    }, {
      x: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7', 'Day 8', 'Day 9', 'Day 10'],
      y: [0, 0, 3, 7, 10, 15, 17, 23, 30, 37],
      type: 'scatter',
      mode: 'lines',
      name: 'Done',
      stackgroup: 'one',
      fillcolor: chartColors.sequential.green[4],
      line: {
        width: 0
      }
    }, {
      x: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7', 'Day 8', 'Day 9', 'Day 10'],
      y: [0, 5, 8, 10, 12, 10, 8, 5, 3, 0],
      type: 'scatter',
      mode: 'lines',
      name: 'In Progress',
      stackgroup: 'one',
      fillcolor: chartColors.sequential.blue[4],
      line: {
        width: 0
      }
    }, {
      x: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7', 'Day 8', 'Day 9', 'Day 10'],
      y: [45, 40, 34, 28, 23, 20, 20, 17, 12, 8],
      type: 'scatter',
      mode: 'lines',
      name: 'To Do',
      stackgroup: 'one',
      fillcolor: chartColors.sequential.blue[2],
      line: {
        width: 0
      }
    }],
    layout: {
      yaxis: {
        title: 'Story Points'
      },
      xaxis: {
        title: 'Sprint Days'
      }
    }
  }
}`,...(F=(E=y.parameters)==null?void 0:E.docs)==null?void 0:F.source}}};var V,_,I;c.parameters={...c.parameters,docs:{...(V=c.parameters)==null?void 0:V.docs,source:{originalSource:`{
  args: {
    title: 'Team Productivity Heatmap',
    data: [{
      z: [[8, 12, 15, 10, 5], [10, 14, 16, 12, 8], [12, 16, 18, 14, 10], [9, 13, 15, 11, 7], [6, 10, 12, 8, 4]],
      x: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
      y: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
      type: 'heatmap',
      colorscale: [[0, chartColors.sequential.green[0]], [0.5, chartColors.sequential.green[4]], [1, chartColors.sequential.green[8]]],
      showscale: true,
      colorbar: {
        title: 'Story Points'
      }
    }],
    layout: {
      xaxis: {
        title: 'Day of Week'
      },
      yaxis: {
        title: 'Sprint Week'
      }
    }
  }
}`,...(I=(_=c.parameters)==null?void 0:_.docs)==null?void 0:I.source}}};var J,K,N;m.parameters={...m.parameters,docs:{...(J=m.parameters)==null?void 0:J.docs,source:{originalSource:`{
  render: () => <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <Chart title="Sprint Velocity" data={[{
      x: ['Sprint 40', 'Sprint 41', 'Sprint 42'],
      y: [35, 48, 42],
      type: 'bar',
      marker: {
        color: chartColors.primary[0]
      }
    }]} layout={{
      ...chartLayouts.bar,
      height: 300
    }} />
      <Chart title="Bug Distribution" data={[{
      values: [15, 42, 89, 156],
      labels: ['Critical', 'High', 'Medium', 'Low'],
      type: 'pie',
      marker: {
        colors: chartColors.categorical.slice(0, 4)
      }
    }]} layout={{
      ...chartLayouts.pie,
      height: 300
    }} />
    </div>
}`,...(N=(K=m.parameters)==null?void 0:K.docs)==null?void 0:N.source}}};const Z=["VelocityTrend","BurndownChart","CycleTimeHistogram","TeamCapacityBar","DefectsByPriority","MonteCarloSimulation","ThroughputScatter","CumulativeFlow","HeatmapProductivity","MultipleCharts"];export{n as BurndownChart,y as CumulativeFlow,r as CycleTimeHistogram,o as DefectsByPriority,c as HeatmapProductivity,s as MonteCarloSimulation,m as MultipleCharts,i as TeamCapacityBar,l as ThroughputScatter,t as VelocityTrend,Z as __namedExportsOrder,Y as default};
