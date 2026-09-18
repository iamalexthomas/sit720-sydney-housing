/* The same scaling, one-hot encoding and KNN averaging as the Python pipeline. */
function validateProperty(input) {
  if (!['Parramatta','Blacktown','Mosman'].includes(input.suburb)) throw Error('Choose one of the three suburbs.');
  if (!['Apartment','House','Townhouse'].includes(input.property_type)) throw Error('Choose a supported property type.');
  const limits = {bedrooms:[0,7],bathrooms:[1,5],parking:[0,6]};
  const row = {...input};
  for (const [key,[low,high]] of Object.entries(limits)) {
    if (key === 'parking' && (input[key] === '' || input[key] == null)) {row[key] = null; continue;}
    if (input[key] === '' || input[key] == null) throw Error('Please enter '+key+'.');
    row[key] = Number(input[key]);
    if (!Number.isInteger(row[key]) || row[key]<low || row[key]>high) throw Error(key+' must be a whole number from '+low+' to '+high+'.');
  }
  if (!/^\d{4}-\d{2}-\d{2}$/.test(input.sale_date)) throw Error('Enter a valid date.');
  const date = new Date(input.sale_date+'T00:00:00Z');
  if (!Number.isFinite(date.getTime()) || date.toISOString().slice(0,10)!==input.sale_date) throw Error('Enter a valid date.');
  return row;
}
function predictProperty(model, input) {
  const row = validateProperty(input);
  const date = new Date(row.sale_date+'T00:00:00Z');
  const numeric = [row.bedrooms,row.bathrooms,row.parking,(date.getUTCFullYear()-2025)*12+date.getUTCMonth(),row.bathrooms/Math.max(row.bedrooms,1)];
  const features = numeric.map((v,i)=>((v==null ? model.medians[i] : v)-model.means[i])/model.scales[i]);
  for (const [i,key] of ['suburb','property_type'].entries()) {
    for (const category of model.categories[i]) features.push(row[key]===category ? 1 : 0);
  }
  const distances = model.training_features.map((training,i)=>({i,d:training.reduce((sum,v,j)=>sum+(v-features[j])**2,0)}));
  distances.forEach(item=>item.d=Math.round(item.d*1e12)/1e12);
  distances.sort((a,b)=>a.d-b.d || a.i-b.i);
  const neighbours = distances.slice(0,model.k);
  const prediction = neighbours.reduce((sum,n)=>sum+model.training_targets[n.i],0)/model.k;
  const warning = row.sale_date<model.metadata.training_min_date || row.sale_date>model.metadata.training_max_date
    ? 'This date is outside the training period. Treat the estimate cautiously; the model has not been tested for future market changes.' : '';
  return {prediction_aud:prediction,warning};
}
if (typeof module !== 'undefined') module.exports = {predictProperty,validateProperty};
