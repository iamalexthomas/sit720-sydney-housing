let fittedModel;
const form = document.querySelector('#property-form');
const button = document.querySelector('#predict-button');
function showPrediction(input) {
  const result = predictProperty(fittedModel,input);
  document.querySelector('#price').textContent = new Intl.NumberFormat('en-AU',{style:'currency',currency:'AUD',maximumFractionDigits:0}).format(result.prediction_aud);
  document.querySelector('#result-note').textContent = input.suburb+' · '+input.property_type+' · '+input.bedrooms+' bedrooms';
  document.querySelector('#input-warning').textContent = result.warning;
  document.querySelector('#error').textContent = '';
  return result;
}
form.addEventListener('submit',event=>{
  event.preventDefault();
  try {showPrediction(Object.fromEntries(new FormData(form)));}
  catch(error){document.querySelector('#error').textContent=error.message;}
});
fetch('model.json').then(response=>{if(!response.ok)throw Error('Model could not be loaded.');return response.json();})
.then(model=>{
  fittedModel=model;button.disabled=false;button.textContent='Predict price';
  if(document.modelContext?.registerTool){
    const lifecycle=new AbortController();
    const registration=document.modelContext.registerTool({
      name:'predict_property_price',description:'Set property details and display the trained model estimate in AUD.',
      inputSchema:{type:'object',properties:{suburb:{type:'string',enum:['Parramatta','Blacktown','Mosman']},property_type:{type:'string',enum:['Apartment','House','Townhouse']},bedrooms:{type:'integer',minimum:0,maximum:7},bathrooms:{type:'integer',minimum:1,maximum:5},parking:{type:['integer','null'],minimum:0,maximum:6},sale_date:{type:'string'}},required:['suburb','property_type','bedrooms','bathrooms','sale_date'],additionalProperties:false},
      annotations:{readOnlyHint:false,untrustedContentHint:false},
      execute(input){const row=validateProperty(input);for(const key of ['suburb','property_type','bedrooms','bathrooms','parking','sale_date'])form.elements[key].value=row[key]??'';return showPrediction(row);}
    },{signal:lifecycle.signal});
    Promise.resolve(registration).catch(()=>{});
    window.addEventListener('pagehide',()=>lifecycle.abort(),{once:true});
  }
}).catch(error=>{document.querySelector('#error').textContent=error.message;button.textContent='Model unavailable';});
