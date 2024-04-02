import React, { useState, useEffect } from 'react';

const ApplianceInfo = () => {
    const [activeTab, setActiveTab] = useState('Refrigerator');
    const [applianceData, setApplianceData] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    const appliances = [
        'Refrigerator',
        'Dish Washer',
        'Washing Machine',
        'Oven',
        'Air Conditioner'
    ];

    const nextPage = () => {
        setCurrentPage(prevPage => Math.min(prevPage + 1, totalPages));
    };

    const prevPage = () => {
        setCurrentPage(prevPage => Math.max(prevPage - 1, 1));
    };
      useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`http://localhost:8000/appliances/${activeTab}?page=${currentPage}`);
                if (!response.ok) {
                    throw new Error(response.statusText);
                }
                const data = await response.json();
                setApplianceData(data);
            } catch (error) {
                console.error("Fetching data error:", error);
            }
        };
    
        fetchData();
    }, [activeTab, currentPage]);
  

    useEffect(() => {
      const fetchTotalPages = async () => {
          try {
              const response = await fetch(`http://localhost:8000/appliances/${activeTab}`);
              if (!response.ok) throw new Error(response.statusText);
              const data = await response.json();
              console.log("Total items data:", data);
              const totalItems = data.length;
              const totalPages = Math.ceil(totalItems / 10);
              setTotalPages(totalPages);
          } catch (error) {
              console.error("Fetching total pages error:", error);
          }
      };
  
      fetchTotalPages();
  }, [activeTab]);
  

    return (
        <div className="App">
            <div className="tabs">
                {appliances.map(appliance => (
                    <button
                        key={appliance}
                        className={`tab-button ${activeTab === appliance ? 'active' : ''}`}
                        onClick={() => {
                            setActiveTab(appliance);
                            setCurrentPage(1);
                        }}
                    >
                        {appliance}
                    </button>
                ))}
            </div>
            <div className="content">
                <table className="appliance-table">
                    <thead>
                        <tr>
                            <th>Model</th>
                            <th>Brand</th>
                            <th>Power Consumed (Kw)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {applianceData.map((item, index) => (
                            <tr key={index}>
                                <td>{item.model_num}</td>
                                <td>{item.brand_name}</td>
                                <td>{item.aec}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <div className="pagination">
                    <button onClick={prevPage} disabled={currentPage === 1}>Previous</button>
                    <span>Page {currentPage} of {totalPages}</span>
                    <button onClick={nextPage} disabled={currentPage === totalPages}>Next</button>
                </div>
            </div>
        </div>
    );
};

export default ApplianceInfo;

