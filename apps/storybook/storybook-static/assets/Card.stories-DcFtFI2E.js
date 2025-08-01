import{j as e}from"./jsx-runtime-D_zvdyIk.js";import{B as g}from"./Button-g3Jj3_oP.js";import{C as s,a as l,b as c,c as o,d,e as b}from"./Card-DGA8wUb9.js";import"./index-0yr9KlQE.js";import"./index-B9jMzQIx.js";import"./index-BwobEAja.js";import"./utils-CytzSlOG.js";const V={title:"Components/Card",component:s,tags:["autodocs"]},r={render:()=>e.jsxs(s,{className:"w-[350px]",children:[e.jsxs(l,{children:[e.jsx(c,{children:"Sprint Velocity"}),e.jsx(o,{children:"Average story points completed per sprint"})]}),e.jsxs(d,{children:[e.jsx("div",{className:"text-4xl font-bold",children:"42"}),e.jsx("p",{className:"text-gray-600 text-sm mt-2",children:"+12% from last quarter"})]})]})},a={render:()=>e.jsxs(s,{className:"w-[350px]",children:[e.jsxs(l,{children:[e.jsx(c,{children:"Project Status"}),e.jsx(o,{children:"Current sprint progress and health"})]}),e.jsx(d,{children:e.jsxs("div",{className:"space-y-2",children:[e.jsxs("div",{className:"flex justify-between",children:[e.jsx("span",{children:"Completed"}),e.jsx("span",{className:"font-semibold",children:"24/30"})]}),e.jsxs("div",{className:"flex justify-between",children:[e.jsx("span",{children:"In Progress"}),e.jsx("span",{className:"font-semibold",children:"4"})]}),e.jsxs("div",{className:"flex justify-between",children:[e.jsx("span",{children:"Blocked"}),e.jsx("span",{className:"font-semibold text-red-600",children:"2"})]})]})}),e.jsx(b,{children:e.jsx(g,{className:"w-full",children:"View Details"})})]})},t={render:()=>e.jsx(s,{className:"w-[250px]",children:e.jsx(d,{className:"p-6",children:e.jsxs("div",{className:"space-y-2",children:[e.jsx("p",{className:"text-sm text-gray-600",children:"Total Story Points"}),e.jsx("p",{className:"text-3xl font-bold text-[#03564c]",children:"1,248"}),e.jsx("p",{className:"text-xs text-gray-500",children:"Last 90 days"})]})})})},n={render:()=>e.jsxs(s,{className:"w-[600px]",children:[e.jsxs(l,{children:[e.jsx(c,{children:"Velocity Trend"}),e.jsx(o,{children:"Story points completed over the last 10 sprints"})]}),e.jsx(d,{children:e.jsx("div",{className:"h-64 bg-gray-100 rounded flex items-center justify-center text-gray-500",children:"Chart placeholder"})})]})};var i,p,m;r.parameters={...r.parameters,docs:{...(i=r.parameters)==null?void 0:i.docs,source:{originalSource:`{
  render: () => <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Sprint Velocity</CardTitle>
        <CardDescription>Average story points completed per sprint</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-4xl font-bold">42</div>
        <p className="text-gray-600 text-sm mt-2">
          +12% from last quarter
        </p>
      </CardContent>
    </Card>
}`,...(m=(p=r.parameters)==null?void 0:p.docs)==null?void 0:m.source}}};var x,C,h;a.parameters={...a.parameters,docs:{...(x=a.parameters)==null?void 0:x.docs,source:{originalSource:`{
  render: () => <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Project Status</CardTitle>
        <CardDescription>Current sprint progress and health</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span>Completed</span>
            <span className="font-semibold">24/30</span>
          </div>
          <div className="flex justify-between">
            <span>In Progress</span>
            <span className="font-semibold">4</span>
          </div>
          <div className="flex justify-between">
            <span>Blocked</span>
            <span className="font-semibold text-red-600">2</span>
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button className="w-full">View Details</Button>
      </CardFooter>
    </Card>
}`,...(h=(C=a.parameters)==null?void 0:C.docs)==null?void 0:h.source}}};var j,N,u;t.parameters={...t.parameters,docs:{...(j=t.parameters)==null?void 0:j.docs,source:{originalSource:`{
  render: () => <Card className="w-[250px]">
      <CardContent className="p-6">
        <div className="space-y-2">
          <p className="text-sm text-gray-600">Total Story Points</p>
          <p className="text-3xl font-bold text-[#03564c]">1,248</p>
          <p className="text-xs text-gray-500">Last 90 days</p>
        </div>
      </CardContent>
    </Card>
}`,...(u=(N=t.parameters)==null?void 0:N.docs)==null?void 0:u.source}}};var f,y,v;n.parameters={...n.parameters,docs:{...(f=n.parameters)==null?void 0:f.docs,source:{originalSource:`{
  render: () => <Card className="w-[600px]">
      <CardHeader>
        <CardTitle>Velocity Trend</CardTitle>
        <CardDescription>Story points completed over the last 10 sprints</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-64 bg-gray-100 rounded flex items-center justify-center text-gray-500">
          Chart placeholder
        </div>
      </CardContent>
    </Card>
}`,...(v=(y=n.parameters)==null?void 0:y.docs)==null?void 0:v.source}}};const F=["Default","WithFooter","MetricCard","ChartCard"];export{n as ChartCard,r as Default,t as MetricCard,a as WithFooter,F as __namedExportsOrder,V as default};
