#ifndef buildingLoads_H
#define buildingLoads_H

#include "fvMeshFunctionObject.H"
#include "volFields.H"
#include "surfaceFields.H"

namespace Foam
{

class buildingLoads : public functionObjects::fvMeshFunctionObject
{
private:
    word patchName_;
    word pressureFieldName_;

    label patchID_;

    void calculateLoads();

public:

    TypeName("buildingLoads");

    buildingLoads(const word& name, const Time& runTime, const dictionary& dict);
    virtual ~buildingLoads() = default;

    // Read configuration
    virtual bool read(const dictionary& dict);

    // Execute
    virtual bool execute();

    // Write
    virtual bool write();
};

}

#endif
