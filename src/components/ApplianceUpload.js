import React, { useState } from 'react';

const ApplianceForm = () => {
  const [energyStickerFile, setEnergyStickerFile] = useState(null);
  const [appliancePhotoFile, setAppliancePhotoFile] = useState(null);
  const [totalCost, setTotalCost] = useState('');
  const [appliances, setAppliances] = useState([]);
  const [predictedAppliance, setPredictedAppliance] = useState('');

  const handleEnergyStickerFileChange = (event) => {
    setEnergyStickerFile(event.target.files[0]);
  };

  const handleAppliancePhotoFileChange = (event) => {
    setAppliancePhotoFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!appliancePhotoFile) {
      alert('Please upload the appliance photo to proceed.');
      return;
    }

    const formData = new FormData();
    if (energyStickerFile) {
      formData.append('energy_sticker', energyStickerFile);  // Only append if file is selected
    }
    formData.append('appliance_photo', appliancePhotoFile);

    try {
      const response = await fetch('http://localhost:8000/upload/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setTotalCost(result.totalCost);
      setAppliances(result.appliances || []);
      setPredictedAppliance(result.predictedClass);
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload the files and calculate the cost.');
    }
  };

  return (
    <div>
      <form className="form-container" onSubmit={handleSubmit}>
        <div className="upload-container">
          <label htmlFor="energy-sticker">Upload Energy Sticker:</label>
          <input type="file" id="energy-sticker" onChange={handleEnergyStickerFileChange}/>
        </div>
        <div className="upload-container">
          <label htmlFor="appliance-photo">Upload Appliance Photo:</label>
          <input type="file" id="appliance-photo" onChange={handleAppliancePhotoFileChange} required />
        </div>
        <button type="submit">Upload and Calculate</button>
      </form>
      {appliances.length > 0 && (
        <div className="results-container">
          <h2>Results</h2>
          <div>Total Cost of Power Consumption for {predictedAppliance}: ${totalCost}</div>
          <div className="cards-container">
            {appliances.map((appliance, index) => (
              <div key={index} className="card">
                <div><strong>Model:</strong> {appliance.model_num}</div>
                <div><strong>Power Consumed:</strong> {appliance.aec} kWh</div>
                <div><strong>Brand:</strong> {appliance.brand_name}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ApplianceForm;
