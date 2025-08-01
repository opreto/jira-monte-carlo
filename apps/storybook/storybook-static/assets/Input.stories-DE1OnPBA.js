import{j as O}from"./jsx-runtime-D_zvdyIk.js";import{r as k}from"./index-0yr9KlQE.js";import{c as z}from"./utils-CytzSlOG.js";const l=k.forwardRef(({className:C,type:F,error:H,...V},q)=>O.jsx("input",{type:F,className:z("flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm","file:border-0 file:bg-transparent file:text-sm file:font-medium","placeholder:text-gray-500","focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#03564c] focus-visible:ring-offset-2","disabled:cursor-not-allowed disabled:opacity-50","transition-colors duration-200",H&&"border-red-500 focus-visible:ring-red-500",C),ref:q,...V}));l.displayName="Input";l.__docgenInfo={description:"",methods:[],displayName:"Input",props:{error:{required:!1,tsType:{name:"boolean"},description:""}}};const J={title:"Primitives/Input",component:l,parameters:{layout:"centered"},tags:["autodocs"],argTypes:{error:{control:{type:"boolean"}},disabled:{control:{type:"boolean"}}}},e={args:{placeholder:"Enter text..."}},r={args:{value:"Hello, Sprint Radar!",onChange:()=>{}}},a={args:{type:"email",placeholder:"email@example.com"}},s={args:{type:"password",placeholder:"Enter password"}},o={args:{type:"number",placeholder:"0",min:0,max:100}},t={args:{error:!0,placeholder:"This field has an error"}},n={args:{disabled:!0,placeholder:"Disabled input"}},c={args:{type:"file",accept:".csv"}};var p,i,d;e.parameters={...e.parameters,docs:{...(p=e.parameters)==null?void 0:p.docs,source:{originalSource:`{
  args: {
    placeholder: 'Enter text...'
  }
}`,...(d=(i=e.parameters)==null?void 0:i.docs)==null?void 0:d.source}}};var m,u,g;r.parameters={...r.parameters,docs:{...(m=r.parameters)==null?void 0:m.docs,source:{originalSource:`{
  args: {
    value: 'Hello, Sprint Radar!',
    onChange: () => {}
  }
}`,...(g=(u=r.parameters)==null?void 0:u.docs)==null?void 0:g.source}}};var f,b,h;a.parameters={...a.parameters,docs:{...(f=a.parameters)==null?void 0:f.docs,source:{originalSource:`{
  args: {
    type: 'email',
    placeholder: 'email@example.com'
  }
}`,...(h=(b=a.parameters)==null?void 0:b.docs)==null?void 0:h.source}}};var y,x,E;s.parameters={...s.parameters,docs:{...(y=s.parameters)==null?void 0:y.docs,source:{originalSource:`{
  args: {
    type: 'password',
    placeholder: 'Enter password'
  }
}`,...(E=(x=s.parameters)==null?void 0:x.docs)==null?void 0:E.source}}};var v,w,S;o.parameters={...o.parameters,docs:{...(v=o.parameters)==null?void 0:v.docs,source:{originalSource:`{
  args: {
    type: 'number',
    placeholder: '0',
    min: 0,
    max: 100
  }
}`,...(S=(w=o.parameters)==null?void 0:w.docs)==null?void 0:S.source}}};var D,I,N;t.parameters={...t.parameters,docs:{...(D=t.parameters)==null?void 0:D.docs,source:{originalSource:`{
  args: {
    error: true,
    placeholder: 'This field has an error'
  }
}`,...(N=(I=t.parameters)==null?void 0:I.docs)==null?void 0:N.source}}};var R,T,W;n.parameters={...n.parameters,docs:{...(R=n.parameters)==null?void 0:R.docs,source:{originalSource:`{
  args: {
    disabled: true,
    placeholder: 'Disabled input'
  }
}`,...(W=(T=n.parameters)==null?void 0:T.docs)==null?void 0:W.source}}};var _,j,P;c.parameters={...c.parameters,docs:{...(_=c.parameters)==null?void 0:_.docs,source:{originalSource:`{
  args: {
    type: 'file',
    accept: '.csv'
  }
}`,...(P=(j=c.parameters)==null?void 0:j.docs)==null?void 0:P.source}}};const K=["Default","WithValue","Email","Password","Number","WithError","Disabled","File"];export{e as Default,n as Disabled,a as Email,c as File,o as Number,s as Password,t as WithError,r as WithValue,K as __namedExportsOrder,J as default};
