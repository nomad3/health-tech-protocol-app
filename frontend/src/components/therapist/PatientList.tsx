import React from 'react';
import { Card, Badge } from '../common';
import type { Patient } from '../../types/therapist';

interface PatientListProps {
  patients: Patient[];
  onPatientClick?: (patient: Patient) => void;
}

const statusColors: Record<string, 'green' | 'amber' | 'gray'> = {
  active: 'green',
  inactive: 'gray',
  completed: 'amber',
};

const PatientList: React.FC<PatientListProps> = ({ patients, onPatientClick }) => {
  return (
    <div className="space-y-3">
      {patients.length === 0 ? (
        <Card>
          <p className="text-gray-500 text-center py-4">No patients found</p>
        </Card>
      ) : (
        patients.map((patient) => (
          <Card
            key={patient.id}
            onClick={() => onPatientClick?.(patient)}
            className="cursor-pointer hover:shadow-md transition-shadow duration-200"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-teal-100 rounded-full flex items-center justify-center">
                    <span className="text-teal-600 font-semibold text-lg">
                      {patient.first_name[0]}{patient.last_name[0]}
                    </span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">
                      {patient.first_name} {patient.last_name}
                    </h4>
                    <p className="text-sm text-gray-600">{patient.email}</p>
                  </div>
                </div>
              </div>
              <Badge variant={statusColors[patient.status]}>
                {patient.status}
              </Badge>
            </div>
          </Card>
        ))
      )}
    </div>
  );
};

export default PatientList;
