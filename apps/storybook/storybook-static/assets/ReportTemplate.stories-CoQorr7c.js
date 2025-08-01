import{j as e}from"./jsx-runtime-D_zvdyIk.js";import{r as x}from"./index-0yr9KlQE.js";import{c as y}from"./utils-CytzSlOG.js";import{P as Y,H as X,a as Z,c as $,M as ee,S as O,C as J,F as te,G as M}from"./Layout-ChYhyPwW.js";import{B as P}from"./Button-g3Jj3_oP.js";import{a as ae,M as b}from"./MetricCard-CHK9-UkR.js";import{T as re,b as ie,c as m,d as p,e as le,f as a}from"./Table-WJkD4t0p.js";import{C as q,a as N}from"./constants-CSgdsXDf.js";import{C as u,d as h,a as A,b as k}from"./Card-DGA8wUb9.js";import"./index-B9jMzQIx.js";import"./index-BwobEAja.js";const c=x.forwardRef(({className:n,title:r,subtitle:i,date:l,logo:o,headerActions:t,footerContent:d,printable:R=!0,children:g,...w},U)=>{const W=l?l instanceof Date?l.toLocaleDateString("en-US",{year:"numeric",month:"long",day:"numeric"}):l:new Date().toLocaleDateString("en-US",{year:"numeric",month:"long",day:"numeric"});return e.jsxs(Y,{ref:U,className:y("bg-white",R&&"print:text-black",n),...w,children:[e.jsxs(X,{className:"print:hidden",children:[e.jsx(Z,{children:o||"Sprint Radar"}),e.jsx($,{children:t||e.jsxs(e.Fragment,{children:[e.jsx(P,{variant:"outline",size:"sm",onClick:()=>window.print(),children:"Print"}),e.jsx(P,{variant:"outline",size:"sm",children:"Export PDF"})]})})]}),e.jsxs(ee,{children:[e.jsx(O,{spacing:"md",children:e.jsx(J,{size:"lg",children:e.jsxs("div",{className:"text-center",children:[e.jsx("h1",{className:"text-3xl font-bold text-gray-900 sm:text-4xl",children:r}),i&&e.jsx("p",{className:"mt-2 text-lg text-gray-600",children:i}),e.jsxs("p",{className:"mt-4 text-sm text-gray-500",children:["Generated on ",W]})]})})}),g]}),e.jsx(te,{className:"print:hidden",children:d||e.jsxs("div",{className:"text-center text-sm text-gray-500",children:["© ",new Date().getFullYear()," Sprint Radar - Enterprise Agile Analytics"]})})]})});c.displayName="ReportTemplate";const s=x.forwardRef(({className:n,title:r,description:i,spacing:l="md",children:o,...t},d)=>e.jsx(O,{ref:d,spacing:l,className:n,...t,children:e.jsxs(J,{size:"lg",children:[(r||i)&&e.jsxs("div",{className:"mb-6",children:[r&&e.jsx("h2",{className:"text-2xl font-bold text-gray-900",children:r}),i&&e.jsx("p",{className:"mt-2 text-gray-600",children:i})]}),o]})}));s.displayName="ReportSection";const T=x.forwardRef(({className:n,highlights:r,children:i,...l},o)=>e.jsxs("div",{ref:o,className:y("rounded-lg border border-gray-200 bg-gray-50 p-6",n),...l,children:[r&&r.length>0&&e.jsx(M,{cols:r.length>3?4:r.length,gap:"md",className:"mb-6",children:r.map((t,d)=>e.jsxs("div",{className:"text-center",children:[e.jsx("p",{className:"text-sm font-medium text-gray-600",children:t.label}),e.jsxs("p",{className:"mt-1 text-2xl font-bold text-gray-900",children:[t.value,t.unit&&e.jsx("span",{className:"ml-1 text-lg font-normal text-gray-600",children:t.unit})]})]},d))}),e.jsx("div",{className:"prose prose-sm max-w-none text-gray-700",children:i})]}));T.displayName="ExecutiveSummary";const S=x.forwardRef(({className:n,metrics:r,columns:i=3,...l},o)=>e.jsx(M,{ref:o,cols:i,gap:"md",className:n,...l,children:r.map((t,d)=>e.jsxs("div",{className:"rounded-lg border border-gray-200 bg-white p-4",children:[e.jsx("p",{className:"text-sm font-medium text-gray-600",children:t.label}),e.jsx("p",{className:"mt-1 text-xl font-bold text-gray-900",children:t.value}),t.change!==void 0&&e.jsxs("p",{className:y("mt-1 text-sm",{"text-green-600":t.trend==="up","text-red-600":t.trend==="down","text-gray-600":t.trend==="neutral"}),children:[t.trend==="up"&&"↑",t.trend==="down"&&"↓",t.trend==="neutral"&&"→"," ",t.change,typeof t.change=="number"&&"%"]})]},d))}));S.displayName="MetricSummary";c.__docgenInfo={description:"",methods:[],displayName:"ReportTemplate",props:{title:{required:!0,tsType:{name:"string"},description:""},subtitle:{required:!1,tsType:{name:"string"},description:""},date:{required:!1,tsType:{name:"union",raw:"string | Date",elements:[{name:"string"},{name:"Date"}]},description:""},logo:{required:!1,tsType:{name:"ReactReactNode",raw:"React.ReactNode"},description:""},headerActions:{required:!1,tsType:{name:"ReactReactNode",raw:"React.ReactNode"},description:""},footerContent:{required:!1,tsType:{name:"ReactReactNode",raw:"React.ReactNode"},description:""},printable:{required:!1,tsType:{name:"boolean"},description:"",defaultValue:{value:"true",computed:!1}}}};s.__docgenInfo={description:"",methods:[],displayName:"ReportSection",props:{title:{required:!1,tsType:{name:"string"},description:""},description:{required:!1,tsType:{name:"string"},description:""},spacing:{required:!1,tsType:{name:"union",raw:"'sm' | 'md' | 'lg'",elements:[{name:"literal",value:"'sm'"},{name:"literal",value:"'md'"},{name:"literal",value:"'lg'"}]},description:"",defaultValue:{value:"'md'",computed:!1}}}};T.__docgenInfo={description:"",methods:[],displayName:"ExecutiveSummary",props:{highlights:{required:!1,tsType:{name:"Array",elements:[{name:"signature",type:"object",raw:`{
  label: string
  value: string | number
  unit?: string
}`,signature:{properties:[{key:"label",value:{name:"string",required:!0}},{key:"value",value:{name:"union",raw:"string | number",elements:[{name:"string"},{name:"number"}],required:!0}},{key:"unit",value:{name:"string",required:!1}}]}}],raw:`Array<{
  label: string
  value: string | number
  unit?: string
}>`},description:""}}};S.__docgenInfo={description:"",methods:[],displayName:"MetricSummary",props:{metrics:{required:!0,tsType:{name:"Array",elements:[{name:"signature",type:"object",raw:`{
  label: string
  value: string | number
  change?: string | number
  trend?: 'up' | 'down' | 'neutral'
}`,signature:{properties:[{key:"label",value:{name:"string",required:!0}},{key:"value",value:{name:"union",raw:"string | number",elements:[{name:"string"},{name:"number"}],required:!0}},{key:"change",value:{name:"union",raw:"string | number",elements:[{name:"string"},{name:"number"}],required:!1}},{key:"trend",value:{name:"union",raw:"'up' | 'down' | 'neutral'",elements:[{name:"literal",value:"'up'"},{name:"literal",value:"'down'"},{name:"literal",value:"'neutral'"}],required:!1}}]}}],raw:`Array<{
  label: string
  value: string | number
  change?: string | number
  trend?: 'up' | 'down' | 'neutral'
}>`},description:""},columns:{required:!1,tsType:{name:"union",raw:"2 | 3 | 4",elements:[{name:"literal",value:"2"},{name:"literal",value:"3"},{name:"literal",value:"4"}]},description:"",defaultValue:{value:"3",computed:!1}}}};const K=x.forwardRef(({title:n,className:r,containerClassName:i,data:l=[],layout:o={},config:t={},responsive:d=!0},R)=>{const g={...o,title:n||o.title},w={responsive:d,displayModeBar:!1,...t};return e.jsx("div",{ref:R,className:y("relative w-full overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm",i),children:e.jsx("div",{"data-plotly":!0,"data-plotly-data":JSON.stringify(l),"data-plotly-layout":JSON.stringify(g),"data-plotly-config":JSON.stringify(w),className:y("w-full bg-gray-50 flex items-center justify-center",r),style:{height:g.height||400},children:e.jsx("div",{className:"text-gray-400",children:"Loading chart..."})})})});K.displayName="ChartSSR";K.__docgenInfo={description:`Server-side rendering safe version of Chart component
Renders a placeholder div that can be hydrated client-side with Plotly`,methods:[],displayName:"ChartSSR",props:{title:{required:!1,tsType:{name:"string"},description:""},className:{required:!1,tsType:{name:"string"},description:""},containerClassName:{required:!1,tsType:{name:"string"},description:""},data:{required:!1,tsType:{name:"Array",elements:[{name:"any"}],raw:"any[]"},description:"",defaultValue:{value:"[]",computed:!1}},layout:{required:!1,tsType:{name:"any"},description:"",defaultValue:{value:"{}",computed:!1}},config:{required:!1,tsType:{name:"any"},description:"",defaultValue:{value:"{}",computed:!1}},responsive:{required:!1,tsType:{name:"boolean"},description:"",defaultValue:{value:"true",computed:!1}}}};const ge={title:"Templates/ReportTemplate",component:c,tags:["autodocs"],parameters:{layout:"fullscreen"}},v={args:{title:"Sprint 42 Performance Report",subtitle:"Team Alpha - Q1 2025",children:e.jsxs(e.Fragment,{children:[e.jsx(s,{title:"Executive Summary",children:e.jsxs(T,{highlights:[{label:"Sprint Velocity",value:42,unit:"points"},{label:"Completion Rate",value:93.3,unit:"%"},{label:"Cycle Time",value:2.8,unit:"days"},{label:"Quality Score",value:"A+"}],children:[e.jsx("p",{children:"Sprint 42 demonstrated strong performance with a 93.3% completion rate, delivering 42 out of 45 committed story points. The team maintained consistency with the 6-sprint average velocity of 42.5 points while achieving the lowest bug rate in the past quarter."}),e.jsx("p",{children:"Key achievements include successful delivery of all critical features, maintaining sub-3-day cycle times, and zero critical bugs in production. The team's collaborative efforts resulted in improved code review turnaround times and enhanced test coverage."})]})}),e.jsx(s,{title:"Key Metrics",children:e.jsx(S,{metrics:[{label:"Stories Completed",value:"15 of 18",trend:"neutral"},{label:"Bug Rate",value:"0.12 per story",change:-25,trend:"down"},{label:"Team Capacity",value:"85%",change:0,trend:"neutral"},{label:"PR Reviews",value:156,change:18,trend:"up"},{label:"Test Coverage",value:"87%",change:3,trend:"up"},{label:"Deploy Frequency",value:"2.3 per day",change:15,trend:"up"}],columns:3})})]})}},f={render:()=>e.jsxs(c,{title:"Q1 2025 Sprint Performance Analysis",subtitle:"Comprehensive Team Performance and Forecasting Report",children:[e.jsx(s,{title:"Executive Summary",spacing:"md",children:e.jsxs(T,{highlights:[{label:"Avg Velocity",value:43.2,unit:"points"},{label:"Predictability",value:94.5,unit:"%"},{label:"Forecast Date",value:"Apr 12"}],children:[e.jsx("p",{children:"The Q1 2025 sprint performance analysis reveals consistent team velocity with an average of 43.2 story points per sprint, representing a 7% improvement over Q4 2024. Team predictability has reached 94.5%, indicating mature estimation practices and stable delivery patterns."}),e.jsx("p",{children:"Based on current velocity trends and Monte Carlo simulations, the project is forecasted to complete by April 12, 2025, with 85% confidence. This represents a two-week improvement from the original baseline estimate."})]})}),e.jsx(s,{title:"Sprint Velocity Trends",spacing:"md",children:e.jsx(u,{children:e.jsx(h,{className:"p-6",children:e.jsx(q,{title:"6-Sprint Velocity Trend",data:[{x:["Sprint 37","Sprint 38","Sprint 39","Sprint 40","Sprint 41","Sprint 42"],y:[46,40,44,35,48,42],type:"scatter",mode:"lines+markers",name:"Completed",line:{color:N.primary[0],width:3},marker:{size:8}},{x:["Sprint 37","Sprint 38","Sprint 39","Sprint 40","Sprint 41","Sprint 42"],y:[48,42,45,40,50,45],type:"scatter",mode:"lines+markers",name:"Committed",line:{color:N.categorical[1],width:2,dash:"dash"},marker:{size:6}}],layout:{height:400,yaxis:{title:"Story Points"}}})})})}),e.jsx(s,{title:"Team Performance Metrics",spacing:"md",children:e.jsxs(ae,{cols:4,children:[e.jsx(b,{title:"Sprint Velocity",value:42,unit:"points",trend:"up",trendValue:5,trendLabel:"vs average",size:"sm"}),e.jsx(b,{title:"Completion Rate",value:"93.3",unit:"%",trend:"up",trendValue:2.3,trendLabel:"vs last sprint",size:"sm"}),e.jsx(b,{title:"Cycle Time",value:2.8,unit:"days",trend:"down",trendValue:-12,trendLabel:"improvement",size:"sm"}),e.jsx(b,{title:"Bug Rate",value:.12,unit:"per story",trend:"down",trendValue:-25,trendLabel:"reduction",size:"sm"})]})}),e.jsx(s,{title:"Sprint Details",spacing:"md",children:e.jsxs(u,{children:[e.jsx(A,{children:e.jsx(k,{children:"Sprint Performance by Team Member"})}),e.jsx(h,{children:e.jsxs(re,{children:[e.jsx(ie,{children:e.jsxs(m,{children:[e.jsx(p,{children:"Team Member"}),e.jsx(p,{children:"Stories Completed"}),e.jsx(p,{children:"Points Delivered"}),e.jsx(p,{children:"Avg Cycle Time"}),e.jsx(p,{children:"Quality Score"})]})}),e.jsxs(le,{children:[e.jsxs(m,{children:[e.jsx(a,{className:"font-medium",children:"Sarah Chen"}),e.jsx(a,{children:"8"}),e.jsx(a,{children:"21"}),e.jsx(a,{children:"2.3 days"}),e.jsx(a,{children:"A+"})]}),e.jsxs(m,{children:[e.jsx(a,{className:"font-medium",children:"Mike Johnson"}),e.jsx(a,{children:"6"}),e.jsx(a,{children:"13"}),e.jsx(a,{children:"3.1 days"}),e.jsx(a,{children:"A"})]}),e.jsxs(m,{children:[e.jsx(a,{className:"font-medium",children:"Emily Davis"}),e.jsx(a,{children:"5"}),e.jsx(a,{children:"18"}),e.jsx(a,{children:"2.8 days"}),e.jsx(a,{children:"A+"})]}),e.jsxs(m,{children:[e.jsx(a,{className:"font-medium",children:"David Kim"}),e.jsx(a,{children:"4"}),e.jsx(a,{children:"8"}),e.jsx(a,{children:"4.2 days"}),e.jsx(a,{children:"B+"})]})]})]})})]})}),e.jsx(s,{title:"Forecasting & Risk Analysis",spacing:"md",children:e.jsxs(M,{cols:2,gap:"lg",children:[e.jsx(u,{children:e.jsx(h,{className:"p-6",children:e.jsx(q,{title:"Monte Carlo Completion Forecast",data:[{x:Array.from({length:100},(n,r)=>new Date(2025,2,1+r)),y:Array.from({length:100},(n,r)=>1/(1+Math.exp(-(r-50)/10))+(Math.random()-.5)*.1),type:"scatter",mode:"lines",name:"Completion Probability",line:{color:N.primary[0],width:3},fill:"tozeroy",fillcolor:"rgba(3, 86, 76, 0.2)"}],layout:{height:300,yaxis:{title:"Probability",tickformat:".0%"},xaxis:{title:"Date"}}})})}),e.jsxs(u,{children:[e.jsx(A,{children:e.jsx(k,{children:"Risk Assessment"})}),e.jsx(h,{children:e.jsxs("div",{className:"space-y-4",children:[e.jsxs("div",{children:[e.jsx("h4",{className:"font-medium text-red-600",children:"High Risk Items"}),e.jsxs("ul",{className:"mt-2 list-inside list-disc space-y-1 text-sm",children:[e.jsx("li",{children:"Technical debt in authentication module"}),e.jsx("li",{children:"Dependency on external API availability"})]})]}),e.jsxs("div",{children:[e.jsx("h4",{className:"font-medium text-yellow-600",children:"Medium Risk Items"}),e.jsxs("ul",{className:"mt-2 list-inside list-disc space-y-1 text-sm",children:[e.jsx("li",{children:"Team member vacation schedule in April"}),e.jsx("li",{children:"Upcoming framework migration"}),e.jsx("li",{children:"Performance optimization requirements"})]})]}),e.jsxs("div",{children:[e.jsx("h4",{className:"font-medium text-green-600",children:"Mitigation Strategies"}),e.jsxs("ul",{className:"mt-2 list-inside list-disc space-y-1 text-sm",children:[e.jsx("li",{children:"Allocate 20% capacity for tech debt"}),e.jsx("li",{children:"Implement circuit breaker for API calls"}),e.jsx("li",{children:"Cross-training for critical components"})]})]})]})})]})]})})]})},C={render:()=>e.jsxs(c,{title:"Weekly Status Report",subtitle:"Week of January 27, 2025",printable:!1,children:[e.jsx(s,{children:e.jsx(S,{metrics:[{label:"Stories In Progress",value:12},{label:"Stories Completed",value:8},{label:"Blockers",value:2},{label:"Team Velocity",value:"85%"}],columns:4})}),e.jsx(s,{children:e.jsxs(u,{children:[e.jsx(A,{children:e.jsx(k,{children:"This Week's Highlights"})}),e.jsx(h,{children:e.jsxs("ul",{className:"list-inside list-disc space-y-2",children:[e.jsx("li",{children:"Completed user authentication feature ahead of schedule"}),e.jsx("li",{children:"Resolved critical performance issue in data processing pipeline"}),e.jsx("li",{children:"Onboarded new team member successfully"}),e.jsx("li",{children:"Achieved 95% test coverage on new features"})]})})]})})]})},j={render:()=>e.jsx(c,{title:"Custom Analytics Report",logo:e.jsxs("div",{className:"flex items-center gap-2",children:[e.jsx("div",{className:"h-8 w-8 rounded bg-[#03564c]"}),e.jsx("span",{className:"font-semibold",children:"My Company"})]}),headerActions:e.jsxs("div",{className:"flex gap-2",children:[e.jsx("button",{className:"text-sm text-gray-600 hover:text-gray-900",children:"Share"}),e.jsx("button",{className:"text-sm text-gray-600 hover:text-gray-900",children:"Download"}),e.jsx("button",{className:"text-sm text-gray-600 hover:text-gray-900",children:"Settings"})]}),footerContent:e.jsxs("div",{className:"flex items-center justify-between text-sm text-gray-500",children:[e.jsx("span",{children:"Confidential - Internal Use Only"}),e.jsx("span",{children:"Page 1 of 1"})]}),children:e.jsx(s,{title:"Custom Content",children:e.jsx("p",{className:"text-gray-600",children:"This demonstrates a report with custom header and footer content."})})})};var H,D,V;v.parameters={...v.parameters,docs:{...(H=v.parameters)==null?void 0:H.docs,source:{originalSource:`{
  args: {
    title: 'Sprint 42 Performance Report',
    subtitle: 'Team Alpha - Q1 2025',
    children: <>
        <ReportSection title="Executive Summary">
          <ExecutiveSummary highlights={[{
          label: 'Sprint Velocity',
          value: 42,
          unit: 'points'
        }, {
          label: 'Completion Rate',
          value: 93.3,
          unit: '%'
        }, {
          label: 'Cycle Time',
          value: 2.8,
          unit: 'days'
        }, {
          label: 'Quality Score',
          value: 'A+'
        }]}>
            <p>
              Sprint 42 demonstrated strong performance with a 93.3% completion rate, 
              delivering 42 out of 45 committed story points. The team maintained 
              consistency with the 6-sprint average velocity of 42.5 points while 
              achieving the lowest bug rate in the past quarter.
            </p>
            <p>
              Key achievements include successful delivery of all critical features, 
              maintaining sub-3-day cycle times, and zero critical bugs in production. 
              The team's collaborative efforts resulted in improved code review 
              turnaround times and enhanced test coverage.
            </p>
          </ExecutiveSummary>
        </ReportSection>

        <ReportSection title="Key Metrics">
          <MetricSummary metrics={[{
          label: 'Stories Completed',
          value: '15 of 18',
          trend: 'neutral'
        }, {
          label: 'Bug Rate',
          value: '0.12 per story',
          change: -25,
          trend: 'down'
        }, {
          label: 'Team Capacity',
          value: '85%',
          change: 0,
          trend: 'neutral'
        }, {
          label: 'PR Reviews',
          value: 156,
          change: 18,
          trend: 'up'
        }, {
          label: 'Test Coverage',
          value: '87%',
          change: 3,
          trend: 'up'
        }, {
          label: 'Deploy Frequency',
          value: '2.3 per day',
          change: 15,
          trend: 'up'
        }]} columns={3} />
        </ReportSection>
      </>
  }
}`,...(V=(D=v.parameters)==null?void 0:D.docs)==null?void 0:V.source}}};var z,I,B;f.parameters={...f.parameters,docs:{...(z=f.parameters)==null?void 0:z.docs,source:{originalSource:`{
  render: () => <ReportTemplate title="Q1 2025 Sprint Performance Analysis" subtitle="Comprehensive Team Performance and Forecasting Report">
      <ReportSection title="Executive Summary" spacing="md">
        <ExecutiveSummary highlights={[{
        label: 'Avg Velocity',
        value: 43.2,
        unit: 'points'
      }, {
        label: 'Predictability',
        value: 94.5,
        unit: '%'
      }, {
        label: 'Forecast Date',
        value: 'Apr 12'
      }]}>
          <p>
            The Q1 2025 sprint performance analysis reveals consistent team velocity 
            with an average of 43.2 story points per sprint, representing a 7% 
            improvement over Q4 2024. Team predictability has reached 94.5%, 
            indicating mature estimation practices and stable delivery patterns.
          </p>
          <p>
            Based on current velocity trends and Monte Carlo simulations, the project 
            is forecasted to complete by April 12, 2025, with 85% confidence. This 
            represents a two-week improvement from the original baseline estimate.
          </p>
        </ExecutiveSummary>
      </ReportSection>

      <ReportSection title="Sprint Velocity Trends" spacing="md">
        <Card>
          <CardContent className="p-6">
            <Chart title="6-Sprint Velocity Trend" data={[{
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
          }]} layout={{
            height: 400,
            yaxis: {
              title: 'Story Points'
            }
          }} />
          </CardContent>
        </Card>
      </ReportSection>

      <ReportSection title="Team Performance Metrics" spacing="md">
        <MetricCardGrid cols={4}>
          <MetricCard title="Sprint Velocity" value={42} unit="points" trend="up" trendValue={5} trendLabel="vs average" size="sm" />
          <MetricCard title="Completion Rate" value="93.3" unit="%" trend="up" trendValue={2.3} trendLabel="vs last sprint" size="sm" />
          <MetricCard title="Cycle Time" value={2.8} unit="days" trend="down" trendValue={-12} trendLabel="improvement" size="sm" />
          <MetricCard title="Bug Rate" value={0.12} unit="per story" trend="down" trendValue={-25} trendLabel="reduction" size="sm" />
        </MetricCardGrid>
      </ReportSection>

      <ReportSection title="Sprint Details" spacing="md">
        <Card>
          <CardHeader>
            <CardTitle>Sprint Performance by Team Member</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Team Member</TableHead>
                  <TableHead>Stories Completed</TableHead>
                  <TableHead>Points Delivered</TableHead>
                  <TableHead>Avg Cycle Time</TableHead>
                  <TableHead>Quality Score</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell className="font-medium">Sarah Chen</TableCell>
                  <TableCell>8</TableCell>
                  <TableCell>21</TableCell>
                  <TableCell>2.3 days</TableCell>
                  <TableCell>A+</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Mike Johnson</TableCell>
                  <TableCell>6</TableCell>
                  <TableCell>13</TableCell>
                  <TableCell>3.1 days</TableCell>
                  <TableCell>A</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Emily Davis</TableCell>
                  <TableCell>5</TableCell>
                  <TableCell>18</TableCell>
                  <TableCell>2.8 days</TableCell>
                  <TableCell>A+</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">David Kim</TableCell>
                  <TableCell>4</TableCell>
                  <TableCell>8</TableCell>
                  <TableCell>4.2 days</TableCell>
                  <TableCell>B+</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </ReportSection>

      <ReportSection title="Forecasting & Risk Analysis" spacing="md">
        <Grid cols={2} gap="lg">
          <Card>
            <CardContent className="p-6">
              <Chart title="Monte Carlo Completion Forecast" data={[{
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
            }]} layout={{
              height: 300,
              yaxis: {
                title: 'Probability',
                tickformat: '.0%'
              },
              xaxis: {
                title: 'Date'
              }
            }} />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Risk Assessment</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-red-600">High Risk Items</h4>
                  <ul className="mt-2 list-inside list-disc space-y-1 text-sm">
                    <li>Technical debt in authentication module</li>
                    <li>Dependency on external API availability</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-yellow-600">Medium Risk Items</h4>
                  <ul className="mt-2 list-inside list-disc space-y-1 text-sm">
                    <li>Team member vacation schedule in April</li>
                    <li>Upcoming framework migration</li>
                    <li>Performance optimization requirements</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-green-600">Mitigation Strategies</h4>
                  <ul className="mt-2 list-inside list-disc space-y-1 text-sm">
                    <li>Allocate 20% capacity for tech debt</li>
                    <li>Implement circuit breaker for API calls</li>
                    <li>Cross-training for critical components</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </Grid>
      </ReportSection>
    </ReportTemplate>
}`,...(B=(I=f.parameters)==null?void 0:I.docs)==null?void 0:B.source}}};var E,F,_;C.parameters={...C.parameters,docs:{...(E=C.parameters)==null?void 0:E.docs,source:{originalSource:`{
  render: () => <ReportTemplate title="Weekly Status Report" subtitle="Week of January 27, 2025" printable={false}>
      <ReportSection>
        <MetricSummary metrics={[{
        label: 'Stories In Progress',
        value: 12
      }, {
        label: 'Stories Completed',
        value: 8
      }, {
        label: 'Blockers',
        value: 2
      }, {
        label: 'Team Velocity',
        value: '85%'
      }]} columns={4} />
      </ReportSection>

      <ReportSection>
        <Card>
          <CardHeader>
            <CardTitle>This Week's Highlights</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-inside list-disc space-y-2">
              <li>Completed user authentication feature ahead of schedule</li>
              <li>Resolved critical performance issue in data processing pipeline</li>
              <li>Onboarded new team member successfully</li>
              <li>Achieved 95% test coverage on new features</li>
            </ul>
          </CardContent>
        </Card>
      </ReportSection>
    </ReportTemplate>
}`,...(_=(F=C.parameters)==null?void 0:F.docs)==null?void 0:_.source}}};var L,Q,G;j.parameters={...j.parameters,docs:{...(L=j.parameters)==null?void 0:L.docs,source:{originalSource:`{
  render: () => <ReportTemplate title="Custom Analytics Report" logo={<div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded bg-[#03564c]" />
          <span className="font-semibold">My Company</span>
        </div>} headerActions={<div className="flex gap-2">
          <button className="text-sm text-gray-600 hover:text-gray-900">
            Share
          </button>
          <button className="text-sm text-gray-600 hover:text-gray-900">
            Download
          </button>
          <button className="text-sm text-gray-600 hover:text-gray-900">
            Settings
          </button>
        </div>} footerContent={<div className="flex items-center justify-between text-sm text-gray-500">
          <span>Confidential - Internal Use Only</span>
          <span>Page 1 of 1</span>
        </div>}>
      <ReportSection title="Custom Content">
        <p className="text-gray-600">
          This demonstrates a report with custom header and footer content.
        </p>
      </ReportSection>
    </ReportTemplate>
}`,...(G=(Q=j.parameters)==null?void 0:Q.docs)==null?void 0:G.source}}};const be=["BasicReport","ComprehensiveReport","MinimalReport","CustomHeaderReport"];export{v as BasicReport,f as ComprehensiveReport,j as CustomHeaderReport,C as MinimalReport,be as __namedExportsOrder,ge as default};
